from app import app, db, User, Medicine

def verify_virat():
    with app.app_context():
        # Trigger seeding
        from app import seed_database
        seed_database()
        
        user = User.query.filter_by(username='virat').first()
        if user:
            print(f"User 'virat' found. Role: {user.role}, Store ID: {user.store_id}")
            med_count = Medicine.query.filter_by(user_id=user.id).count()
            print(f"Medicine Count for 'virat': {med_count}")
            if med_count > 100:
                print("SUCCESS: Virat has full inventory.")
            else:
                print("WARNING: Virat has incomplete inventory.")
        else:
            print("ERROR: User 'virat' not found.")

if __name__ == "__main__":
    verify_virat()
