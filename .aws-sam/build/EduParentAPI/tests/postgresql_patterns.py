"""
PostgreSQL Patterns and Common Operations
Quick reference for database operations in EduParent app
"""
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.services.auth_service import get_password_hash, verify_password


# ====================
# DATABASE CONNECTION
# ====================

def get_db_session() -> Session:
    """Get a database session"""
    return SessionLocal()


# ====================
# CREATE OPERATIONS
# ====================

def create_user(email: str, password: str, full_name: str = None) -> User:
    """Create a new user"""
    db = get_db_session()
    try:
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def bulk_create_users(users_data: list) -> int:
    """Create multiple users at once"""
    db = get_db_session()
    try:
        users = [
            User(
                email=data["email"],
                hashed_password=get_password_hash(data["password"]),
                full_name=data.get("full_name")
            )
            for data in users_data
        ]
        db.add_all(users)
        db.commit()
        return len(users)
    finally:
        db.close()


# ====================
# READ OPERATIONS
# ====================

def get_user_by_id(user_id: int) -> User:
    """Get user by ID"""
    db = get_db_session()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


def get_user_by_email(email: str) -> User:
    """Get user by email"""
    db = get_db_session()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()


def get_active_users(limit: int = 10) -> list[User]:
    """Get active users with limit"""
    db = get_db_session()
    try:
        return db.query(User).filter(
            User.is_active == True
        ).limit(limit).all()
    finally:
        db.close()


def search_users_by_name(name_pattern: str) -> list[User]:
    """Search users by name pattern"""
    db = get_db_session()
    try:
        return db.query(User).filter(
            User.full_name.ilike(f"%{name_pattern}%")
        ).all()
    finally:
        db.close()


def get_users_count() -> dict:
    """Get user statistics"""
    db = get_db_session()
    try:
        total = db.query(User).count()
        active = db.query(User).filter(User.is_active == True).count()
        inactive = total - active
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive
        }
    finally:
        db.close()


def get_recent_users(days: int = 7, limit: int = 10) -> list[User]:
    """Get recently created users"""
    from datetime import datetime, timedelta
    
    db = get_db_session()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return db.query(User).filter(
            User.created_at >= cutoff_date
        ).order_by(User.created_at.desc()).limit(limit).all()
    finally:
        db.close()


# ====================
# UPDATE OPERATIONS
# ====================

def update_user_info(user_id: int, **updates) -> User:
    """Update user information"""
    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()


def update_user_password(user_id: int, new_password: str) -> bool:
    """Update user password"""
    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.hashed_password = get_password_hash(new_password)
            db.commit()
            return True
        return False
    finally:
        db.close()


def deactivate_user(user_id: int) -> bool:
    """Soft delete - deactivate user"""
    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            db.commit()
            return True
        return False
    finally:
        db.close()


def bulk_update_users(filter_condition, update_data: dict) -> int:
    """Bulk update users matching condition"""
    db = get_db_session()
    try:
        updated_count = db.query(User).filter(
            filter_condition
        ).update(update_data, synchronize_session=False)
        db.commit()
        return updated_count
    finally:
        db.close()


# ====================
# DELETE OPERATIONS
# ====================

def delete_user(user_id: int) -> bool:
    """Hard delete - remove user from database"""
    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
    finally:
        db.close()


def delete_inactive_users() -> int:
    """Delete all inactive users"""
    db = get_db_session()
    try:
        deleted_count = db.query(User).filter(
            User.is_active == False
        ).delete(synchronize_session=False)
        db.commit()
        return deleted_count
    finally:
        db.close()


# ====================
# TRANSACTION PATTERNS
# ====================

def transfer_user_data_transaction(from_user_id: int, to_user_id: int):
    """Example of transaction handling"""
    db = get_db_session()
    try:
        # Start transaction (automatic)
        from_user = db.query(User).filter(User.id == from_user_id).first()
        to_user = db.query(User).filter(User.id == to_user_id).first()
        
        if not from_user or not to_user:
            raise ValueError("User not found")
        
        # Perform multiple operations
        from_user.is_active = False
        # In real app, you might transfer user progress, etc.
        
        # Commit all changes atomically
        db.commit()
        return True
        
    except Exception as e:
        # Rollback on any error
        db.rollback()
        print(f"Transaction failed: {e}")
        return False
    finally:
        db.close()


# ====================
# AUTHENTICATION HELPERS
# ====================

def authenticate_user(email: str, password: str) -> User:
    """Authenticate user with email and password"""
    user = get_user_by_email(email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def check_email_exists(email: str) -> bool:
    """Check if email is already registered"""
    user = get_user_by_email(email)
    return user is not None


# ====================
# USAGE EXAMPLES
# ====================

if __name__ == "__main__":
    """Example usage of the patterns"""
    
    print("📋 PostgreSQL Patterns Examples")
    print("=" * 40)
    
    # Create users
    print("\n1. Creating users...")
    user1 = create_user("alice@example.com", "password123", "Alice Johnson")
    user2 = create_user("bob@example.com", "password456", "Bob Smith")
    
    if user1:
        print(f"✅ Created: {user1.email}")
    if user2:
        print(f"✅ Created: {user2.email}")
    
    # Read operations
    print("\n2. Reading users...")
    stats = get_users_count()
    print(f"✅ User stats: {stats}")
    
    active_users = get_active_users(limit=5)
    print(f"✅ Active users: {len(active_users)}")
    
    # Search
    alice_users = search_users_by_name("Alice")
    print(f"✅ Found {len(alice_users)} users named Alice")
    
    # Update
    print("\n3. Updating users...")
    if user1:
        updated = update_user_info(user1.id, full_name="Alice Cooper")
        if updated:
            print(f"✅ Updated {updated.email} to {updated.full_name}")
    
    # Authentication
    print("\n4. Authentication...")
    auth_user = authenticate_user("alice@example.com", "password123")
    if auth_user:
        print(f"✅ Authenticated: {auth_user.email}")
    
    # Cleanup
    print("\n5. Cleanup...")
    if user1:
        delete_user(user1.id)
        print(f"✅ Deleted user {user1.id}")
    if user2:
        delete_user(user2.id)
        print(f"✅ Deleted user {user2.id}")
    
    print("\n🎉 Examples complete!")
    print("\nTo use in your code:")
    print("from tests.postgresql_patterns import create_user, get_user_by_email")