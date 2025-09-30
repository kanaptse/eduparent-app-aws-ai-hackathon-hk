"""
Simple PostgreSQL CRUD Operations Example
Demonstrates Create, Read, Update, Delete operations using the existing database
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.database import get_db, engine, SessionLocal
from app.models.user import User
from app.services.auth_service import get_password_hash, verify_password


def demo_crud_operations():
    """Demonstrate CRUD operations with PostgreSQL"""
    print("🧪 PostgreSQL CRUD Operations Demo")
    print("=" * 50)
    
    # Use the existing database session
    db = SessionLocal()
    
    try:
        # === CREATE Operation ===
        print("\n📝 CREATE Operation")
        print("-" * 20)
        
        user = User(
            email="demo@eduparent.com",
            hashed_password=get_password_hash("demopassword123"),
            full_name="Demo User"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Created user:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Full Name: {user.full_name}")
        print(f"   Created At: {user.created_at}")
        print(f"   Is Active: {user.is_active}")
        
        user_id = user.id
        
        # === READ Operations ===
        print("\n📖 READ Operations")
        print("-" * 20)
        
        # Read by ID
        found_user = db.query(User).filter(User.id == user_id).first()
        print(f"✅ Found user by ID {user_id}: {found_user.email}")
        
        # Read by email
        found_by_email = db.query(User).filter(User.email == "demo@eduparent.com").first()
        print(f"✅ Found user by email: {found_by_email.full_name}")
        
        # Read all users (limited)
        all_users = db.query(User).limit(5).all()
        print(f"✅ Total users in database (showing first 5): {len(all_users)}")
        for u in all_users:
            print(f"   - {u.email} ({u.full_name or 'No name'}) - Active: {u.is_active}")
        
        # Count users
        total_count = db.query(User).count()
        active_count = db.query(User).filter(User.is_active == True).count()
        print(f"✅ Database statistics:")
        print(f"   - Total users: {total_count}")
        print(f"   - Active users: {active_count}")
        
        # === UPDATE Operations ===
        print("\n✏️ UPDATE Operations")
        print("-" * 20)
        
        # Update user information
        user.full_name = "Updated Demo User"
        user.email = "updated.demo@eduparent.com"
        db.commit()
        db.refresh(user)
        
        print(f"✅ Updated user:")
        print(f"   New Full Name: {user.full_name}")
        print(f"   New Email: {user.email}")
        print(f"   Updated At: {user.updated_at}")
        
        # Update password
        new_password = "newdemopassword456"
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        # Verify password change
        if verify_password(new_password, user.hashed_password):
            print("✅ Password updated successfully")
        else:
            print("❌ Password update failed")
        
        # Soft delete (deactivate)
        user.is_active = False
        db.commit()
        print(f"✅ User deactivated (soft delete): is_active = {user.is_active}")
        
        # === Advanced Queries ===
        print("\n🔍 Advanced Queries")
        print("-" * 20)
        
        # Query with conditions
        active_users = db.query(User).filter(User.is_active == True).all()
        print(f"✅ Active users: {len(active_users)}")
        
        # Query with ordering
        recent_users = db.query(User).order_by(User.created_at.desc()).limit(3).all()
        print(f"✅ Most recent users:")
        for u in recent_users:
            print(f"   - {u.email} (created: {u.created_at.strftime('%Y-%m-%d %H:%M')})")
        
        # Query with LIKE
        demo_users = db.query(User).filter(User.email.like("%demo%")).all()
        print(f"✅ Users with 'demo' in email: {len(demo_users)}")
        
        # Raw SQL query
        result = db.execute(
            text("SELECT COUNT(*) as count, is_active FROM users GROUP BY is_active")
        ).fetchall()
        print("✅ User statistics (raw SQL):")
        for row in result:
            status = "Active" if row.is_active else "Inactive"
            print(f"   - {status}: {row.count} users")
        
        # === Bulk Operations ===
        print("\n📦 Bulk Operations")
        print("-" * 20)
        
        # Bulk insert
        bulk_users = [
            User(
                email=f"bulk{i}@eduparent.com",
                hashed_password=get_password_hash(f"bulkpass{i}"),
                full_name=f"Bulk User {i}"
            )
            for i in range(1, 4)
        ]
        
        db.add_all(bulk_users)
        db.commit()
        print(f"✅ Bulk inserted {len(bulk_users)} users")
        
        # Bulk update
        updated_count = db.query(User).filter(
            User.email.like("bulk%")
        ).update(
            {"full_name": "Bulk Demo User"},
            synchronize_session=False
        )
        db.commit()
        print(f"✅ Bulk updated {updated_count} users")
        
        # === DELETE Operation ===
        print("\n🗑️ DELETE Operations")
        print("-" * 20)
        
        # Hard delete the demo user
        db.delete(user)
        db.commit()
        print("✅ Demo user hard deleted from database")
        
        # Clean up bulk users
        deleted_count = db.query(User).filter(
            User.email.like("bulk%")
        ).delete(synchronize_session=False)
        db.commit()
        print(f"✅ Cleaned up {deleted_count} bulk demo users")
        
        # Verify deletion
        remaining_demo = db.query(User).filter(
            User.email.like("%demo%")
        ).count()
        print(f"✅ Remaining demo users: {remaining_demo}")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        db.rollback()
        
    finally:
        db.close()
        print("\n✅ Database session closed")


def demo_transaction_management():
    """Demonstrate transaction management"""
    print("\n🔄 Transaction Management Demo")
    print("=" * 40)
    
    db = SessionLocal()
    
    try:
        # Start a transaction
        print("Starting transaction...")
        
        user1 = User(
            email="transaction1@eduparent.com",
            hashed_password=get_password_hash("pass1"),
            full_name="Transaction User 1"
        )
        db.add(user1)
        db.flush()  # Send to DB but don't commit
        print("✅ Added user1 to transaction")
        
        user2 = User(
            email="transaction2@eduparent.com",
            hashed_password=get_password_hash("pass2"),
            full_name="Transaction User 2"
        )
        db.add(user2)
        db.flush()
        print("✅ Added user2 to transaction")
        
        # Commit the transaction
        db.commit()
        print("✅ Transaction committed successfully")
        
        # Clean up
        db.query(User).filter(
            User.email.like("transaction%")
        ).delete(synchronize_session=False)
        db.commit()
        print("✅ Cleaned up transaction demo users")
        
    except Exception as e:
        print(f"❌ Transaction failed: {e}")
        db.rollback()
        print("✅ Transaction rolled back")
        
    finally:
        db.close()


def demo_database_info():
    """Show database connection and schema information"""
    print("\n🔧 Database Information")
    print("=" * 30)
    
    try:
        with engine.connect() as connection:
            # Database version
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL Version: {version[:80]}...")
            
            # Current database
            result = connection.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"✅ Current Database: {db_name}")
            
            # Tables in schema
            result = connection.execute(
                text("""
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
                """)
            )
            tables = result.fetchall()
            print(f"✅ Tables in public schema:")
            for table in tables:
                print(f"   - {table.table_name} ({table.table_type})")
            
            # Columns in users table
            result = connection.execute(
                text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'users' AND table_schema = 'public'
                ORDER BY ordinal_position
                """)
            )
            columns = result.fetchall()
            print(f"✅ Columns in 'users' table:")
            for col in columns:
                nullable = "NULL" if col.is_nullable == "YES" else "NOT NULL"
                default = f" DEFAULT {col.column_default}" if col.column_default else ""
                print(f"   - {col.column_name}: {col.data_type} {nullable}{default}")
                
    except Exception as e:
        print(f"❌ Database info error: {e}")


if __name__ == "__main__":
    """Run the CRUD demo"""
    demo_database_info()
    demo_crud_operations()
    demo_transaction_management()
    
    print("\n" + "=" * 50)
    print("🎉 PostgreSQL CRUD Demo Complete!")
    print("=" * 50)
    print("\nTo run as a pytest:")
    print("uv run pytest tests/test_postgresql_crud_simple.py -v -s")