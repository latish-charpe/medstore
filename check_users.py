from app import app, db, Medicine, User

def check_users():
    with app.app_context():
        users = User.query.all()
        print(f"Total Users: {len(users)}")
        
        for user in users:
            count = Medicine.query.filter_by(user_id=user.id).count()
            print(f"User {user.username} (ID: {user.id}, Role: {user.role}): {count} medicines")
            
        # Check global duplicates (same name, different user)
        meds = Medicine.query.all()
        name_counts = {}
        for med in meds:
            name = med.name.strip().lower()
            name_counts[name] = name_counts.get(name, 0) + 1
            
        dups = {name: count for name, count in name_counts.items() if count > 1}
        print(f"Global Duplicates (Same name across any user): {len(dups)} names duplicated.")
        
        # If we have global duplicates, we might want to delete them from all but one user
        # ideally the 'admin' or the first one.

if __name__ == "__main__":
    check_users()
