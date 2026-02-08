from app import app, db, User

def check_latish():
    with app.app_context():
        user = User.query.filter_by(username='Latish').first()
        if user:
            print(f"User: {user.username}, Role: {user.role}")
            if user.role != 'store_manager':
                print("Updating role to 'store_manager'...")
                user.role = 'store_manager'
                db.session.commit()
                print("Role updated successfully.")
        else:
            print("User 'Latish' not found.")
            # List all users
            users = User.query.all()
            print("Existing users:", [(u.username, u.role) for u in users])

if __name__ == "__main__":
    check_latish()
