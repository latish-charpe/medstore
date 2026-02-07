import requests
import hashlib

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

def log(msg):
    print(msg)
    with open("verify_real_output.txt", "a") as f:
        f.write(msg + "\n")

def test_real_data_seeding():
    # 1. Register New Use 'store_real_01'
    username = "store_real_01"
    password = "password123"
    SECRET_CODE = "medstore2026"
    
    log(f"Registering {username}...")
    resp = session.post(f"{BASE_URL}/register", data={
        "username": username,
        "password": password,
        "confirm_password": password,
        "secret_code": SECRET_CODE,
        "name": "Real Store Manager"
    })
    
    # 2. Login
    log("Logging in...")
    login_resp = session.post(f"{BASE_URL}/login", data={
        "username": username,
        "password": password
    })
    
    if "Dashboard" in login_resp.text or login_resp.url.endswith("/dashboard"):
        log("Login Successful & Dashboard Reached.")
    else:
        log("Login Failed.")
        return

    # 3. Check Dashboard Counts
    # We expect roughly 120-130 medicines
    # We can inspect the HTML for "Total Medicines: X"
    # Or just search for known medicines in the page source
    
    known_meds = [
        "Paracetamol 500mg", "Cetirizine 10mg", "Metformin 500", 
        "Amlodipine 5mg", "Limcee Vitamin C", "Betnovate C",
        "Dabur Chyawanprash", "Zinc Syrup", "ORS Powder",
        "Digital Thermometer", "Whey Protein", "Manforce Pack"
    ]
    
    success_count = 0
    dashboard_html = login_resp.text
    
    for med in known_meds:
        if med in dashboard_html:
            log(f"SUCCESS: Found '{med}' in Dashboard.")
            success_count += 1
        else:
            log(f"FAILURE: '{med}' NOT found in Dashboard.")
            
    if success_count == len(known_meds):
        log("ALL TEST MEDICINES FOUND.")
    else:
        log(f"FOUND {success_count}/{len(known_meds)} TEST MEDICINES.")

    # 4. Check Categories
    # Check 'Sexual Wellness'
    log("Checking Category: Sexual Wellness...")
    resp = session.get(f"{BASE_URL}/healthcare", params={"category": "Sexual Wellness"})
    if "Condoms (Regular)" in resp.text and "Durex Pack" in resp.text:
       log("SUCCESS: Category 'Sexual Wellness' is populated.")
    else:
       log("FAILURE: Category 'Sexual Wellness' is empty or missing items.")

    # Check 'Diabetes Essentials'
    log("Checking Category: Diabetes Essentials...")
    resp = session.get(f"{BASE_URL}/healthcare", params={"category": "Diabetes Essentials"})
    if "Metformin 500" in resp.text and "Insulin Injection" in resp.text:
       log("SUCCESS: Category 'Diabetes Essentials' is populated.")
    else:
       log("FAILURE: Category 'Diabetes Essentials' is empty or missing items.")

if __name__ == "__main__":
    with open("verify_real_output.txt", "w") as f:
        f.write("Starting Real Data Verification...\n")
    try:
        test_real_data_seeding()
    except Exception as e:
        log(f"Error: {e}")
