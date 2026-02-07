from app import app, db, Medicine

def global_deduplicate():
    with app.app_context():
        print("Starting GLOBAL deduplication...")
        
        meds = Medicine.query.all()
        # Track seen names
        seen_names = set()
        duplicates = []
        
        count_kept = 0
        
        for med in meds:
            name = med.name.strip().lower()
            if name in seen_names:
                duplicates.append(med)
            else:
                seen_names.add(name)
                count_kept += 1
                
        print(f"Found {len(duplicates)} duplicates. Keeping {count_kept} unique medicines.")
        
        if duplicates:
            print("Deleting duplicates...")
            for dup in duplicates:
                db.session.delete(dup)
            db.session.commit()
            print("Duplicates deleted.")
        else:
            print("No duplicates found.")

if __name__ == "__main__":
    global_deduplicate()
