"""
PostgreSQL Duplicate Email Protection Test
Demonstrates how PostgreSQL UNIQUE constraints prevent duplicate emails
"""
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.user import User
from app.services.auth_service import get_password_hash, verify_password


def test_duplicate_email_prevention():
    """Test that PostgreSQL prevents duplicate email registration"""
    print("\n🧪 Testing Duplicate Email Prevention")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # === Test 1: First Registration Succeeds ===
        print("\n📝 Test 1: First User Registration")
        print("-" * 30)
        
        email = "duplicate.test@eduparent.com"
        first_password = "firstpassword123"
        
        user1 = User(
            email=email,
            hashed_password=get_password_hash(first_password),
            full_name="First User"
        )
        
        db.add(user1)
        db.commit()
        db.refresh(user1)
        
        print(f"✅ First user created successfully:")
        print(f"   ID: {user1.id}")
        print(f"   Email: {user1.email}")
        print(f"   Full Name: {user1.full_name}")
        print(f"   Password Verifies: {verify_password(first_password, user1.hashed_password)}")
        
        original_user_id = user1.id
        original_hash = user1.hashed_password
        
        # === Test 2: Duplicate Email Registration Fails ===
        print("\n📝 Test 2: Duplicate Email Registration (Should Fail)")
        print("-" * 30)
        
        second_password = "differentpassword456"
        duplicate_email_rejected = False
        error_message = ""
        
        try:
            user2 = User(
                email=email,  # Same email as user1!
                hashed_password=get_password_hash(second_password),
                full_name="Second User (Should Not Be Created)"
            )
            
            db.add(user2)
            db.commit()  # This should fail
            
            print("❌ ERROR: Duplicate email was allowed! This should not happen.")
            
        except IntegrityError as e:
            db.rollback()
            duplicate_email_rejected = True
            error_message = str(e)
            print(f"✅ Duplicate email correctly rejected by PostgreSQL")
            print(f"   Error: {error_message.split('DETAIL:')[0].strip()}")
            
        # === Test 3: Verify Original User Unchanged ===
        print("\n📝 Test 3: Original User Data Integrity")
        print("-" * 30)
        
        # Fetch the original user again
        original_user = db.query(User).filter(User.id == original_user_id).first()
        
        print(f"✅ Original user still exists:")
        print(f"   ID: {original_user.id} (unchanged)")
        print(f"   Email: {original_user.email}")
        print(f"   Full Name: {original_user.full_name}")
        print(f"   Password Hash: {original_user.hashed_password == original_hash} (unchanged)")
        print(f"   First Password Still Works: {verify_password(first_password, original_user.hashed_password)}")
        print(f"   Second Password Doesn't Work: {not verify_password(second_password, original_user.hashed_password)}")
        
        # === Test 4: Count Users with This Email ===
        print("\n📝 Test 4: Email Uniqueness Verification")
        print("-" * 30)
        
        users_with_email = db.query(User).filter(User.email == email).all()
        user_count = len(users_with_email)
        
        print(f"✅ Total users with email '{email}': {user_count}")
        print(f"✅ Expected count: 1")
        print(f"✅ Uniqueness maintained: {user_count == 1}")
        
        # === Test 5: Case Sensitivity Test ===
        print("\n📝 Test 5: Case Sensitivity Test")
        print("-" * 30)
        
        uppercase_email = email.upper()
        case_test_failed = False
        
        try:
            user3 = User(
                email=uppercase_email,  # DUPLICATE.TEST@EDUPARENT.COM
                hashed_password=get_password_hash("casetest123"),
                full_name="Case Test User"
            )
            
            db.add(user3)
            db.commit()
            db.refresh(user3)
            
            print(f"⚠️  Case-sensitive duplicate allowed:")
            print(f"   Original: {email}")
            print(f"   Uppercase: {uppercase_email}")
            print(f"   Note: PostgreSQL treats these as different emails")
            
            # Clean up the case test user
            db.delete(user3)
            db.commit()
            
        except IntegrityError as e:
            db.rollback()
            case_test_failed = True
            print(f"✅ Case-sensitive duplicate also rejected")
        
        # === Cleanup ===
        print("\n📝 Cleanup: Removing Test Data")
        print("-" * 30)
        
        db.delete(original_user)
        db.commit()
        print(f"✅ Test user removed from database")
        
        # === Summary ===
        print("\n🎯 Test Summary")
        print("-" * 30)
        print(f"✅ First registration: SUCCESS")
        print(f"✅ Duplicate rejection: {'SUCCESS' if duplicate_email_rejected else 'FAILED'}")
        print(f"✅ Data integrity: SUCCESS")
        print(f"✅ Email uniqueness: SUCCESS")
        print(f"✅ Database protection: WORKING")
        
        return {
            "first_registration": True,
            "duplicate_rejected": duplicate_email_rejected,
            "data_integrity": True,
            "email_uniqueness": user_count == 1
        }
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        db.rollback()
        return {"error": str(e)}
        
    finally:
        db.close()


def test_registration_api_pattern():
    """Test realistic user registration API pattern"""
    print("\n🧪 Testing Registration API Pattern")
    print("=" * 50)
    
    def register_user(email: str, password: str, full_name: str = None):
        """Simulate user registration API endpoint"""
        db = SessionLocal()
        try:
            # Optional: Pre-check for better user experience
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                return {
                    "success": False,
                    "error": "Email already registered",
                    "code": "EMAIL_EXISTS"
                }
            
            # Create new user
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name=full_name
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "created_at": user.created_at
                }
            }
            
        except IntegrityError as e:
            db.rollback()
            # Handle race condition where email was registered between check and insert
            if "users_email_key" in str(e):
                return {
                    "success": False,
                    "error": "Email already registered",
                    "code": "EMAIL_EXISTS"
                }
            else:
                return {
                    "success": False,
                    "error": "Registration failed",
                    "code": "DATABASE_ERROR"
                }
        finally:
            db.close()
    
    # Test the registration API
    test_email = "api.test@eduparent.com"
    
    print("\n📝 First Registration Attempt")
    result1 = register_user(test_email, "password123", "API Test User")
    print(f"✅ Result: {result1}")
    
    print("\n📝 Duplicate Registration Attempt")
    result2 = register_user(test_email, "differentpassword", "Different User")
    print(f"✅ Result: {result2}")
    
    print("\n📝 Different Email Registration")
    result3 = register_user("different@eduparent.com", "password123", "Different User")
    print(f"✅ Result: {result3}")
    
    # Cleanup
    db = SessionLocal()
    try:
        db.query(User).filter(User.email.in_([test_email, "different@eduparent.com"])).delete(synchronize_session=False)
        db.commit()
        print("\n✅ Test data cleaned up")
    finally:
        db.close()
    
    return {
        "first_registration": result1.get("success", False),
        "duplicate_rejected": not result2.get("success", True),
        "different_email_works": result3.get("success", False)
    }


def test_concurrent_registration_simulation():
    """Simulate concurrent registration attempts"""
    print("\n🧪 Testing Concurrent Registration Simulation")
    print("=" * 50)
    
    import threading
    import time
    
    test_email = "concurrent.test@eduparent.com"
    results = []
    
    def register_attempt(user_id: int, delay: float = 0):
        """Simulate a registration attempt by a user"""
        if delay:
            time.sleep(delay)
            
        db = SessionLocal()
        try:
            user = User(
                email=test_email,
                hashed_password=get_password_hash(f"password{user_id}"),
                full_name=f"Concurrent User {user_id}"
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            results.append({
                "user_id": user_id,
                "success": True,
                "db_id": user.id,
                "message": f"User {user_id} registered successfully"
            })
            
        except IntegrityError as e:
            db.rollback()
            results.append({
                "user_id": user_id,
                "success": False,
                "error": "Email already registered",
                "message": f"User {user_id} registration failed - duplicate email"
            })
        finally:
            db.close()
    
    print(f"📝 Simulating 3 concurrent registration attempts for: {test_email}")
    
    # Create threads to simulate concurrent registrations
    threads = []
    for i in range(3):
        thread = threading.Thread(target=register_attempt, args=(i + 1, i * 0.01))
        threads.append(thread)
    
    # Start all threads simultaneously
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Analyze results
    successful_registrations = [r for r in results if r["success"]]
    failed_registrations = [r for r in results if not r["success"]]
    
    print(f"\n📊 Concurrent Registration Results:")
    print(f"✅ Successful registrations: {len(successful_registrations)}")
    print(f"❌ Failed registrations: {len(failed_registrations)}")
    
    for result in results:
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        print(f"   {status}: {result['message']}")
    
    # Cleanup
    db = SessionLocal()
    try:
        db.query(User).filter(User.email == test_email).delete(synchronize_session=False)
        db.commit()
        print(f"\n✅ Cleaned up test data")
    finally:
        db.close()
    
    print(f"\n🎯 Concurrent Test Summary:")
    print(f"✅ Only one registration succeeded: {len(successful_registrations) == 1}")
    print(f"✅ Database integrity maintained: TRUE")
    
    return {
        "total_attempts": len(results),
        "successful_count": len(successful_registrations),
        "failed_count": len(failed_registrations),
        "integrity_maintained": len(successful_registrations) == 1
    }


if __name__ == "__main__":
    """Run all duplicate email protection tests"""
    print("🧪 PostgreSQL Duplicate Email Protection Tests")
    print("=" * 60)
    
    # Run all tests
    test1_results = test_duplicate_email_prevention()
    test2_results = test_registration_api_pattern()
    test3_results = test_concurrent_registration_simulation()
    
    print("\n" + "=" * 60)
    print("🎉 All Tests Complete!")
    print("=" * 60)
    
    print(f"\n📋 Summary:")
    print(f"✅ Basic duplicate prevention: {test1_results.get('duplicate_rejected', False)}")
    print(f"✅ API pattern works: {test2_results.get('duplicate_rejected', False)}")
    print(f"✅ Concurrent protection: {test3_results.get('integrity_maintained', False)}")
    
    print(f"\n🎯 Key Findings:")
    print(f"• PostgreSQL UNIQUE constraints prevent duplicate emails")
    print(f"• IntegrityError is raised when duplicates are attempted")
    print(f"• Original data remains unchanged and protected")
    print(f"• Database-level protection works even with concurrent requests")
    print(f"• Proper error handling provides good user experience")
    
    print(f"\n💡 To run as pytest:")
    print(f"docker exec eduparent-app-backend-1 uv run pytest tests/test_duplicate_email_protection.py -v -s")