from app import app, Medicine, Category, db

def test_search():
    with app.app_context():
        print("--- Testing Search Logic ---")
        
        # Test 1: Search by name
        search_query = 'Dolo'
        results = Medicine.query.filter(Medicine.name.ilike(f'%{search_query}%')).all()
        print(f"Name search '{search_query}':Found {len(results)} items")
        
        # Test 2: Search by ingredient (Paracetamol)
        search_query = 'Paracetamol'
        results = Medicine.query.filter(
            db.or_(
                Medicine.name.ilike(f'%{search_query}%'),
                Medicine.composition.ilike(f'%{search_query}%')
            )
        ).all()
        print(f"Ingredient search '{search_query}': Found {len(results)} items")
        
        # Test 3: Search by use (headache)
        search_query = 'headache'
        results = Medicine.query.filter(
            db.or_(
                Medicine.name.ilike(f'%{search_query}%'),
                Medicine.composition.ilike(f'%{search_query}%')
            )
        ).all()
        print(f"Use search '{search_query}': Found {len(results)} items")

if __name__ == "__main__":
    test_search()
