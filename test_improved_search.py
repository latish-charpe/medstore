from app import app, db
from models import Medicine, Category

def test_search():
    with app.app_context():
        print("--- Improved Healthcare Search Verification ---")
        
        test_cases = [
            ("paracetamol", ["Dolo 650mg", "Crocin Advance", "Combiflam"]), # Ingredients/Formulation
            ("pain relief", ["Moov Pain Relief"]), # Name
            ("antiseptic", ["Dettol Liquid", "Savlon Antiseptic", "Betadine Ointment"]), # Name/Category
            ("tablet", ["Dolo 650mg", "Crocin Advance", "Calpol 500mg"]), # Type
            ("boric", ["Boroline Cream"]), # Ingredient
            ("xyz-no-match", []) # Empty result
        ]
        
        for search_query, expected_parts in test_cases:
            from sqlalchemy import or_
            query = Medicine.query.join(Category).filter(
                or_(
                    Medicine.name.ilike(f'%{search_query}%'),
                    Medicine.composition.ilike(f'%{search_query}%'),
                    Medicine.medicine_type.ilike(f'%{search_query}%'),
                    Category.name.ilike(f'%{search_query}%')
                )
            )
            results = query.all()
            result_names = [r.name for r in results]
            
            print(f"\nSearch Query: '{search_query}'")
            print(f"Results Found: {len(result_names)}")
            
            if expected_parts:
                found_expected = [name for name in expected_parts if any(name.lower() in r.lower() for r in result_names)]
                if len(found_expected) == len(expected_parts):
                    print(f"PASS: Found all expected samples: {found_expected}")
                else:
                    print(f"FAIL: Missing expected samples. Found {found_expected} of {expected_parts}")
                    print(f"Actual results: {result_names[:5]}...")
            elif not result_names:
                print("PASS: No results found as expected.")
            else:
                print(f"FAIL: Expected no results but found {len(result_names)}.")

        print("\nVerification Complete.")

if __name__ == "__main__":
    test_search()
