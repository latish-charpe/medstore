from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash

def test_login_persistence():
    with app.app_context():
        username = "test_user_repro"
        password = "test_password"
        
        # 1. Clean up potentially existing user
        existing = User.query.filter_by(username=username).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            print(f"Deleted existing test user: {username}")

        # 2. Register
        print(f"Registering {username}...")
        new_user = User(username=username, password_hash=generate_password_hash(password), role='store_manager')
        db.session.add(new_user)
        db.session.commit()
        
        user_id = new_user.id
        print(f"User registered with ID: {user_id}")
        
        # 3. Verify Login (Check Password)
        fetched_user = User.query.get(user_id)
        if fetched_user and check_password_hash(fetched_user.password_hash, password):
            print("Login Check 1: SUCCESS (Immediated after registration)")
        else:
            print("Login Check 1: FAILED")
            return

        # 4. Simulate Logout (Nothing DB side, just to be sure we query again)
        db.session.remove()
        
        # 5. Verify Login Again
        fetched_user_2 = User.query.filter_by(username=username).first()
        if fetched_user_2:
             print(f"User found after session remove: {fetched_user_2.username}")
             if check_password_hash(fetched_user_2.password_hash, password):
                 print("Login Check 2: SUCCESS (After 'logout' simulation)")
             else:
                 print("Login Check 2: FAILED (Password mismatch)")
        else:
             print("Login Check 2: FAILED (User not found)")

if __name__ == '__main__':
    test_login_persistence()
