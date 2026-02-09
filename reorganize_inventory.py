from app import app, db, User, Medicine
from datetime import datetime, timedelta
import random

def reorganize_inventory():
    with app.app_context():
        print("Starting Inventory Cleanup...")
        
        # 1. Deduplication per User
        users = User.query.filter_by(role='store_manager').all()
        
        for user in users:
            print(f"Processing Store: {user.username}")
            meds = Medicine.query.filter_by(user_id=user.id).all()
            
            # Map name -> list of medicines
            med_map = {}
            for med in meds:
                if med.name not in med_map:
                    med_map[med.name] = []
                med_map[med.name].append(med)
            
            for name, duplicates in med_map.items():
                if len(duplicates) > 1:
                    print(f"  Mergin {len(duplicates)} duplicates for '{name}'...")
                    # Sort by expiry (descending) to keep best one
                    duplicates.sort(key=lambda x: x.expiry_date, reverse=True)
                    
                    keeper = duplicates[0]
                    total_qty = sum(d.quantity for d in duplicates)
                    keeper.quantity = total_qty
                    
                    # Delete others
                    for d in duplicates[1:]:
                        db.session.delete(d)
        
        db.session.commit()
        print("Deduplication Complete.")
        
        # 2. Status Enforcement (Randomized subset)
        # We want a mix of statuses for testing
        
        all_meds = Medicine.query.all()
        random.shuffle(all_meds)
        
        total = len(all_meds)
        # 10% Out of Stock
        # 10% Expired
        # 10% Near Expiry
        # 70% Safe/In Stock
        
        out_stock_count = int(total * 0.1)
        expired_count = int(total * 0.1)
        near_expiry_count = int(total * 0.1)
        
        cursor = 0
        
        # Set Out of Stock
        for i in range(cursor, cursor + out_stock_count):
            all_meds[i].quantity = 0
        cursor += out_stock_count
        print(f"Marked {out_stock_count} medicines as Out of Stock.")
        
        # Set Expired (30 days ago)
        for i in range(cursor, cursor + expired_count):
            all_meds[i].expiry_date = datetime.today().date() - timedelta(days=30)
        cursor += expired_count
        print(f"Marked {expired_count} medicines as Expired.")

        # Set Near Expiry (15 days from now)
        for i in range(cursor, cursor + near_expiry_count):
            all_meds[i].expiry_date = datetime.today().date() + timedelta(days=15)
        cursor += near_expiry_count
        print(f"Marked {near_expiry_count} medicines as Near Expiry.")
        
        # Ensure remaining are Safe and In Stock
        for i in range(cursor, total):
            # Reset expiry to safe future if needed (e.g. 1 year)
            if all_meds[i].expiry_date < datetime.today().date() + timedelta(days=60):
                 all_meds[i].expiry_date = datetime.today().date() + timedelta(days=365)
            # Ensure at least some stock
            if all_meds[i].quantity == 0:
                 all_meds[i].quantity = 10
                 
        db.session.commit()
        print("Status Updates Complete.")

if __name__ == "__main__":
    reorganize_inventory()
