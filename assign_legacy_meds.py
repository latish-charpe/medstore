from app import app, db, User, Medicine

def assign_medicines_to_virat():
    with app.app_context():
        # Find default manager 'virat'
        virat = User.query.filter_by(username='virat').first()
        if not virat:
            print("Creating 'virat' if not exists...")
            from app import seed_database
            seed_database()
            virat = User.query.filter_by(username='virat').first()
        
        if not virat:
             print("Error: Could not find or create user 'virat'.")
             return

        print(f"Assigning ALL existing medicines to virat (ID: {virat.id})...")
        
        # Check count before
        total_meds = Medicine.query.count()
        virat_meds = Medicine.query.filter_by(user_id=virat.id).count()
        print(f"Total Medicines: {total_meds}")
        print(f"Virat's Medicines (Before): {virat_meds}")

        # Update all medicines where user_id is NOT virat.id or is NULL
        # Start transaction to update
        try:
             # Find meds not owned by virat
             meds_to_update = Medicine.query.filter(Medicine.user_id != virat.id).all()
             for med in meds_to_update:
                 med.user_id = virat.id
             
             db.session.commit()
             print(f"Updated {len(meds_to_update)} medicines to belong to virat.")
             
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    assign_medicines_to_virat()
