from app import app, db, User, Medicine
from datetime import datetime, timedelta

def verify_cleanup():
    with app.app_context():
        print("Verifying Inventory Cleanup...")
        
        virat = User.query.filter_by(username='virat').first()
        if not virat:
            print("Error: User 'virat' not found.")
            return

        meds = Medicine.query.filter_by(user_id=virat.id).all()
        total = len(meds)
        print(f"Total Medicines for 'virat': {total}")
        
        # Check Duplicates
        names = [m.name for m in meds]
        if len(names) == len(set(names)):
             print("PASS: No duplicate names found.")
        else:
             print(f"FAIL: Duplicates found! {len(names)} vs {len(set(names))} unique.")

        # Check Statuses
        out_stock = sum(1 for m in meds if m.quantity == 0)
        expired = sum(1 for m in meds if m.expiry_status == 'Expired')
        near_expiry = sum(1 for m in meds if m.expiry_status == 'Near Expiry')
        safe = sum(1 for m in meds if m.expiry_status == 'Safe')
        
        print(f"Stats:")
        print(f" - Out of Stock: {out_stock}")
        print(f" - Expired: {expired}")
        print(f" - Near Expiry: {near_expiry}")
        print(f" - Safe: {safe}")
        
        if out_stock > 0 and expired > 0 and near_expiry > 0:
            print("PASS: Status distribution verified.")
        else:
            print("WARNING: Some statuses might be missing.")

if __name__ == "__main__":
    verify_cleanup()
