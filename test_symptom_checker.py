from app import app, smart_symptom_match

def test_symptom_logic():
    print("Testing Universal & Accurate 3-Level Logic...")
    
    test_cases = [
        # LEVEL 1: Acute
        ("fever", ["Paracetamol", "Dolo"], True, "Level 1: Fever"),
        ("cold", ["Cetrizine", "Vicks", "Sinarest"], True, "Level 1: Cold"),
        ("tonsils", ["Betadine Gargle", "Benadryl", "Ascoril"], True, "Level 1: Tonsils"),
        ("diarrhea", ["ORS", "Loperamide"], True, "Level 1: Diarrhea"),
        ("itching", ["Calamine", "Cetrizine"], True, "Level 1: Itching"),
        
        # HEART SAFE MODE
        ("chest pain", ["Supportive Care Only"], True, "Heart: Chest Pain"),
        ("heart attack", [], False, "Heart: Heart Attack (Zero Meds)"),
        ("burning in chest", ["Digene Syrup", "Supportive Care Only"], True, "Heart: Burning/Acidity"),
        
        # LEVEL 2: Chronic / Sensitive / Lifestyle
        ("hair fall", ["Multivitamins", "Vitamin B-complex / B12", "Iron / Calcium"], True, "Level 2: Hair Fall"),
        ("diabetes", ["Multivitamins", "Vitamin B-complex / B12", "Iron / Calcium"], True, "Level 2: Diabetes"),
        ("cancer", ["Multivitamins", "Vitamin B-complex / B12", "Iron / Calcium"], True, "Level 2: Cancer"),
        ("sexual problems", ["Multivitamins", "Vitamin B-complex / B12", "Iron / Calcium"], True, "Level 2: Sexual Problems"),
        ("insomnia", ["Multivitamins", "Vitamin B-complex / B12"], True, "Level 2: Insomnia"),
        ("panic attacks", ["Multivitamins", "Vitamin B-complex / B12"], True, "Level 2: Panic Attacks"),
        ("migraine", ["Multivitamins", "Vitamin B-complex / B12"], True, "Level 2: Migraine"),
        ("hypertension", [], False, "Heart: Hypertension (Zero Meds)"),
        ("low blood pressure", ["ORS", "Supportive Care Only"], True, "Heart: Hypotension (ORS)"),
        ("stroke", [], False, "Heart: Stroke (Zero Meds)"),
        ("anemia", ["Iron / Calcium"], True, "Level 2: Anemia"),
        ("constipation", ["Isabgol", "Lactulose"], True, "Level 1: Constipation"),
        ("acne", ["Benzoyl Peroxide"], True, "Level 1: Acne"),
        ("uti", ["Multivitamins", "Vitamin B-complex / B12"], True, "Level 2: UTI"),
        ("high blood pressure", [], False, "Heart: High BP (Safe Mode)"),
        
        # LEVEL 3: Unknown / Complex / rare
        ("rare medical condition xyz", [], False, "Level 3: Unknown"),
        ("random gibberish", [], False, "Level 3: Random"),
    ]
    
    with app.app_context():
        success_count = 0
        print(f"{'Test Case':<25} | {'Result':<10} | {'Meds Found':<10}")
        print("-" * 55)
        
        for query, expected_meds, expect_meds_flag, description in test_cases:
            results = smart_symptom_match(query)
            
            if not results:
                print(f"{description:<25} | FAIL       | No results")
                continue
                
            found_expected = False
            # We check if ANY of the result segments match our expectation for this level
            for res in results:
                meds = res.get('medicines', [])
                meds_exist = len(meds) > 0
                
                # Verify meds match if expected
                meds_match = True
                if expected_meds:
                    for em in expected_meds:
                        if not any(em in m for m in meds):
                            meds_match = False
                            break
                
                if (meds_exist == expect_meds_flag) and meds_match:
                    found_expected = True
                    break
            
            if found_expected:
                print(f"{description:<25} | PASS       | {'Yes' if expect_meds_flag else 'No'}")
                success_count += 1
            else:
                print(f"{description:<25} | FAIL       | Incorrect meds/flag")
        
        print(f"\nUpgrade Verification: {success_count}/{len(test_cases)} Passed")

if __name__ == "__main__":
    test_symptom_logic()
