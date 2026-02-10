from app import app, db
from models import Medicine, User

def verify_composition():
    with app.app_context():
        print("--- Medicine Composition Verification ---")
        
        # 1. Check Seeding for known brands
        dolo = Medicine.query.filter_by(name='Dolo 650mg').first()
        if dolo:
            print(f"Dolo 650mg Composition: {dolo.composition}")
            if dolo.composition == "Paracetamol IP 650 mg":
                print("PASS: Seeding for Dolo worked.")
            else:
                print("FAIL: Seeding for Dolo mismatch.")
        else:
            print("INFO: Dolo 650mg not found (might need re-seeding).")

        combiflam = Medicine.query.filter_by(name='Combiflam').first()
        if combiflam:
            print(f"Combiflam Composition: {combiflam.composition}")
            if "Ibuprofen" in str(combiflam.composition):
                print("PASS: Seeding for Combiflam worked.")
        
        # 2. Check empty fallback
        generic = Medicine.query.filter(Medicine.composition == None).first()
        if generic:
            print(f"Generic Medicine ({generic.name}) has no composition. (Expected for fallback test)")
        else:
            print("INFO: All medicines have compositions.")

        print("\nVerification Complete.")

if __name__ == "__main__":
    verify_composition()
