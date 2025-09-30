"""
PostgreSQL CRUD Operations Example
Demonstrates Create, Read, Update, Delete operations with the User model
"""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os

from app.db.database import Base, get_db
from app.models.user import User
from app.services.auth_service import get_password_hash, verify_password


# Test Database Setup
@pytest.fixture(scope="function")
def test_db():
    """Create a test database session for each test"""
    # Use the same PostgreSQL instance but a different database name for testing
    DATABASE_URL = os.getenv(
        "TEST_DATABASE_URL", 
        "postgresql://eduparent:password@localhost:5432/eduparent_test"
    )
    
    engine = create_engine(DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up - drop all tables
        Base.metadata.drop_all(bind=engine)


class TestUserCRUD:
    """Test CRUD operations for User model"""
    
    def test_create_user(self, test_db):
        """CREATE: Test creating a new user"""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": get_password_hash("password123"),
            "full_name": "Test User"
        }
        
        # Act - Create user
        user = User(**user_data)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Assert
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.created_at is not None
        assert verify_password("password123", user.hashed_password)
        print(f"✅ Created user with ID: {user.id}")
    
    def test_read_user_by_id(self, test_db):
        """READ: Test retrieving user by ID"""
        # Arrange - Create a user first
        user = User(
            email="read@example.com",
            username="readuser",
            hashed_password=get_password_hash("password123"),
            full_name="Read Test User"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        user_id = user.id
        
        # Act - Read user by ID
        found_user = test_db.query(User).filter(User.id == user_id).first()
        
        # Assert
        assert found_user is not None
        assert found_user.id == user_id
        assert found_user.email == "read@example.com"
        print(f"✅ Found user by ID: {found_user.email}")
    
    def test_read_user_by_email(self, test_db):
        """READ: Test retrieving user by email"""
        # Arrange
        user = User(
            email="unique@example.com",
            username="uniqueuser",
            hashed_password=get_password_hash("password123")
        )
        test_db.add(user)
        test_db.commit()
        
        # Act - Read user by email
        found_user = test_db.query(User).filter(User.email == "unique@example.com").first()
        
        # Assert
        assert found_user is not None
        assert found_user.email == "unique@example.com"
        assert found_user.username == "uniqueuser"
        print(f"✅ Found user by email: {found_user.username}")
    
    def test_read_multiple_users(self, test_db):
        """READ: Test retrieving multiple users with filtering"""
        # Arrange - Create multiple users
        users = [
            User(email="user1@example.com", username="user1", hashed_password=get_password_hash("pass1")),
            User(email="user2@example.com", username="user2", hashed_password=get_password_hash("pass2")),
            User(email="user3@example.com", username="user3", hashed_password=get_password_hash("pass3"), is_active=False)
        ]
        for user in users:
            test_db.add(user)
        test_db.commit()
        
        # Act & Assert - Read all users
        all_users = test_db.query(User).all()
        assert len(all_users) == 3
        print(f"✅ Found {len(all_users)} total users")
        
        # Act & Assert - Read only active users
        active_users = test_db.query(User).filter(User.is_active == True).all()
        assert len(active_users) == 2
        print(f"✅ Found {len(active_users)} active users")
        
        # Act & Assert - Read with ordering
        ordered_users = test_db.query(User).order_by(User.created_at.desc()).all()
        assert len(ordered_users) == 3
        print(f"✅ Retrieved users ordered by creation date")
    
    def test_update_user(self, test_db):
        """UPDATE: Test updating user information"""
        # Arrange - Create user
        user = User(
            email="update@example.com",
            username="updateuser",
            hashed_password=get_password_hash("oldpassword"),
            full_name="Old Name"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Act - Update user
        user.full_name = "New Name"
        user.email = "newemail@example.com"
        test_db.commit()
        test_db.refresh(user)
        
        # Assert
        assert user.full_name == "New Name"
        assert user.email == "newemail@example.com"
        assert user.updated_at is not None
        print(f"✅ Updated user: {user.full_name} ({user.email})")
    
    def test_update_user_password(self, test_db):
        """UPDATE: Test updating user password"""
        # Arrange
        user = User(
            email="password@example.com",
            username="passworduser",
            hashed_password=get_password_hash("oldpassword")
        )
        test_db.add(user)
        test_db.commit()
        
        # Act - Update password
        new_hashed_password = get_password_hash("newpassword123")
        user.hashed_password = new_hashed_password
        test_db.commit()
        test_db.refresh(user)
        
        # Assert
        assert verify_password("newpassword123", user.hashed_password)
        assert not verify_password("oldpassword", user.hashed_password)
        print("✅ Password updated successfully")
    
    def test_soft_delete_user(self, test_db):
        """UPDATE: Test soft delete (deactivate user)"""
        # Arrange
        user = User(
            email="softdelete@example.com",
            username="softdeleteuser",
            hashed_password=get_password_hash("password123")
        )
        test_db.add(user)
        test_db.commit()
        assert user.is_active is True
        
        # Act - Soft delete (deactivate)
        user.is_active = False
        test_db.commit()
        
        # Assert
        assert user.is_active is False
        # User still exists in database
        found_user = test_db.query(User).filter(User.id == user.id).first()
        assert found_user is not None
        assert found_user.is_active is False
        print("✅ User soft deleted (deactivated)")
    
    def test_hard_delete_user(self, test_db):
        """DELETE: Test hard delete (remove from database)"""
        # Arrange
        user = User(
            email="harddelete@example.com",
            username="harddeleteuser",
            hashed_password=get_password_hash("password123")
        )
        test_db.add(user)
        test_db.commit()
        user_id = user.id
        
        # Act - Hard delete
        test_db.delete(user)
        test_db.commit()
        
        # Assert
        found_user = test_db.query(User).filter(User.id == user_id).first()
        assert found_user is None
        print("✅ User hard deleted (removed from database)")
    
    def test_bulk_operations(self, test_db):
        """Advanced: Test bulk insert and update operations"""
        # Arrange - Bulk insert
        users_data = [
            {"email": f"bulk{i}@example.com", "username": f"bulk{i}", 
             "hashed_password": get_password_hash(f"pass{i}")}
            for i in range(1, 6)
        ]
        
        # Act - Bulk insert
        users = [User(**data) for data in users_data]
        test_db.add_all(users)
        test_db.commit()
        
        # Assert - Check bulk insert
        count = test_db.query(User).filter(User.email.like("bulk%")).count()
        assert count == 5
        print(f"✅ Bulk inserted {count} users")
        
        # Act - Bulk update
        test_db.query(User).filter(User.email.like("bulk%")).update(
            {"full_name": "Bulk Updated User"}, 
            synchronize_session=False
        )
        test_db.commit()
        
        # Assert - Check bulk update
        updated_users = test_db.query(User).filter(User.email.like("bulk%")).all()
        for user in updated_users:
            assert user.full_name == "Bulk Updated User"
        print("✅ Bulk updated users")
    
    def test_transaction_rollback(self, test_db):
        """Advanced: Test transaction rollback on error"""
        # Arrange
        initial_count = test_db.query(User).count()
        
        try:
            # Act - Start transaction
            user1 = User(
                email="transaction1@example.com",
                username="trans1",
                hashed_password=get_password_hash("pass1")
            )
            test_db.add(user1)
            test_db.flush()  # Send to DB but don't commit
            
            # This should cause a constraint violation (duplicate email)
            user2 = User(
                email="transaction1@example.com",  # Same email!
                username="trans2",
                hashed_password=get_password_hash("pass2")
            )
            test_db.add(user2)
            test_db.commit()  # This should fail
            
        except IntegrityError:
            test_db.rollback()
            print("✅ Transaction rolled back due to constraint violation")
        
        # Assert - No users should be added
        final_count = test_db.query(User).count()
        assert final_count == initial_count
        print("✅ Database state unchanged after rollback")
    
    def test_complex_queries(self, test_db):
        """Advanced: Test complex SQL queries"""
        # Arrange - Create test data
        users = [
            User(email="query1@example.com", username="query1", 
                 hashed_password=get_password_hash("pass1"),
                 created_at=datetime(2024, 1, 1)),
            User(email="query2@example.com", username="query2", 
                 hashed_password=get_password_hash("pass2"),
                 created_at=datetime(2024, 1, 15)),
            User(email="query3@example.com", username="query3", 
                 hashed_password=get_password_hash("pass3"),
                 created_at=datetime(2024, 2, 1),
                 is_active=False)
        ]
        test_db.add_all(users)
        test_db.commit()
        
        # Act & Assert - Complex queries
        
        # 1. Count by status
        active_count = test_db.query(User).filter(User.is_active == True).count()
        inactive_count = test_db.query(User).filter(User.is_active == False).count()
        print(f"✅ Active users: {active_count}, Inactive users: {inactive_count}")
        
        # 2. Date range query
        from datetime import date
        jan_users = test_db.query(User).filter(
            User.created_at >= datetime(2024, 1, 1),
            User.created_at < datetime(2024, 2, 1)
        ).all()
        assert len(jan_users) == 2
        print(f"✅ Users created in January: {len(jan_users)}")
        
        # 3. Email domain query
        example_users = test_db.query(User).filter(
            User.email.like("%@example.com")
        ).count()
        print(f"✅ Users with @example.com domain: {example_users}")
        
        # 4. Raw SQL query example
        result = test_db.execute(
            text("SELECT COUNT(*) as user_count FROM users WHERE is_active = true")
        ).fetchone()
        print(f"✅ Raw SQL active user count: {result.user_count}")


class TestPostgreSQLFeatures:
    """Test PostgreSQL specific features"""
    
    def test_json_field_operations(self, test_db):
        """Test JSON field storage and querying (if you extend User model)"""
        # Note: This would require adding a JSON field to User model
        # For now, this is a placeholder showing the concept
        
        # Example of how you could store preferences as JSON
        user = User(
            email="json@example.com",
            username="jsonuser",
            hashed_password=get_password_hash("password123")
        )
        test_db.add(user)
        test_db.commit()
        
        print("✅ JSON field operations would go here")
        print("   (Requires adding JSON field to User model)")
    
    def test_database_constraints(self, test_db):
        """Test database constraints and error handling"""
        
        # Test unique email constraint
        user1 = User(
            email="constraint@example.com",
            username="user1",
            hashed_password=get_password_hash("pass1")
        )
        test_db.add(user1)
        test_db.commit()
        
        # Try to create user with same email
        with pytest.raises(IntegrityError):
            user2 = User(
                email="constraint@example.com",  # Duplicate!
                username="user2",
                hashed_password=get_password_hash("pass2")
            )
            test_db.add(user2)
            test_db.commit()
        
        test_db.rollback()
        print("✅ Email uniqueness constraint enforced")


def test_database_connection():
    """Test basic database connection"""
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://eduparent:password@localhost:5432/eduparent"
    )
    
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version[:50]}...")
            
            # Test basic table existence
            result = connection.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = [row[0] for row in result.fetchall()]
            print(f"✅ Available tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise


if __name__ == "__main__":
    """Run individual tests for demonstration"""
    print("🧪 PostgreSQL CRUD Examples")
    print("=" * 50)
    
    # Test basic connection
    test_database_connection()
    print()
    
    print("To run full test suite:")
    print("cd /app && python -m pytest tests/test_postgresql_crud.py -v")