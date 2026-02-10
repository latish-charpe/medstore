from app import app, db
from models import Medicine
from medicines_data import REAL_MEDICINES_DB

def update_compositions():
    with app.app_context():
        print("Updating compositions for existing medicines...")
        for item in REAL_MEDICINES_DB:
            if 'comp' in item:
                # Find all medicines with this name and update their composition
                meds = Medicine.query.filter_by(name=item['name']).all()
                for med in meds:
                    if not med.composition:
                        med.composition = item['comp']
                        print(f"Updated {med.name} with composition: {item['comp']}")
        db.session.commit()
        print("Update complete.")

if __name__ == "__main__":
    update_compositions()
