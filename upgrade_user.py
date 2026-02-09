from app import app, db, User

def upgrade_user(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            user.role = 'store_manager'
            db.session.commit()
            print(f"User {username} upgraded to store_manager.")
        else:
            print(f"User {username} not found.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        upgrade_user(sys.argv[1])
    else:
        upgrade_user('zandu')
