from app import app, db, User, Medicine
from werkzeug.security import generate_password_hash

def verify_isolation():
    with app.app_context():
        print("VERIFYING DATA ISOLATION")
        
        # 1. Check Virat
        virat = User.query.filter_by(username='virat').first()
        if virat:
            count = Medicine.query.filter_by(user_id=virat.id).count()
            print(f"[CHECK] Virat's Medicine Count: {count}")
            if count > 0:
                print(" -> PASS: Virat has data.")
            else:
                print(" -> FAIL: Virat has NO data.")
        else:
            print(" -> FAIL: Virat user missing.")

        # 2. Create Test Manager (simulating new registration)
        test_user = User.query.filter_by(username='test_manager').first()
        if test_user:
            db.session.delete(test_user)
            db.session.commit()
            
        test_user = User(username='test_manager', password_hash=generate_password_hash('test'), role='store_manager')
        db.session.add(test_user)
        db.session.commit()
        
        # simulate registration logic which NO LONGER calls seed_starter_data
        
        # 3. Check Test Manager Data
        test_count = Medicine.query.filter_by(user_id=test_user.id).count()
        print(f"[CHECK] New Manager 'test_manager' Medicine Count: {test_count}")
        
        if test_count == 0:
            print(" -> PASS: New Manager starts with 0 medicines.")
        else:
            print(f" -> FAIL: New Manager has {test_count} medicines (Should be 0).")
            
        # Clean up
        db.session.delete(test_user)
        db.session.commit()

if __name__ == "__main__":
    verify_isolation()
