from app import app, db, Medicine, User

def reset_inventory(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            # Delete all medicines for this user
            Medicine.query.filter_by(user_id=user.id).delete()
            db.session.commit()
            print(f"Inventory cleared for {username}. Login again to re-seed.")
        else:
            print(f"User {username} not found.")

if __name__ == "__main__":
    reset_inventory('laty')
