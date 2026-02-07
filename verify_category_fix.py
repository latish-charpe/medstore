import requests
import time

BASE_URL = "http://127.0.0.1:5000"
CODE = "medstore2026"
USERNAME = f"store_cat_{int(time.time())}"

def log(msg):
    with open("verify_category_output.txt", "a") as f:
        f.write(msg + "\n")
    print(msg)

def test_category_view():
    with open("verify_category_output.txt", "w") as f:
        f.write("Starting Category Verification...\n")
    
    session = requests.Session()
    
    # 1. Register
    log(f"Registering {USERNAME}...")
    reg_payload = {
        "username": USERNAME,
        "password": "password123",
        "confirm_password": "password123",
        "secret_code": CODE
    }
    resp = session.post(f"{BASE_URL}/register", data=reg_payload)
    
    # 2. Login
    log("Logging in...")
    login_payload = {
        "username": USERNAME,
        "password": "password123"
    }
    resp = session.post(f"{BASE_URL}/login", data=login_payload)
    
    if "Dashboard" in resp.text:
        log("Login Successful.")
    else:
        log("Login Failed.")
        return

    # 3. Check /healthcare?category=Pain Relief
    log("Checking /healthcare?category=Pain Relief...")
    resp = session.get(f"{BASE_URL}/healthcare?category=Pain Relief")
    
    if "Paracetamol 650" in resp.text:
        log("SUCCESS: Found 'Paracetamol 650' in Healthcare Category View.")
    else:
        log("FAILURE: 'Paracetamol 650' NOT found in Healthcare Category View.")
        # log(resp.text)

    # 4. Check /medicines?category=Pain Relief
    log("Checking /medicines?category=Pain Relief...")
    resp = session.get(f"{BASE_URL}/medicines?category=Pain Relief")
    
    if "Paracetamol 650" in resp.text:
        log("SUCCESS: Found 'Paracetamol 650' in Medicines Category View.")
    else:
        log("FAILURE: 'Paracetamol 650' NOT found in Medicines Category View.")

    # 5. Check /healthcare?category=Vitamins (Renamed from Vitamin Store)
    log("Checking /healthcare?category=Vitamins...")
    resp = session.get(f"{BASE_URL}/healthcare?category=Vitamins")
    if "Limcee Vitamin C" in resp.text:
         log("SUCCESS: Found 'Limcee Vitamin C' in Vitamins Category.")
    else:
         log("FAILURE: 'Limcee Vitamin C' NOT found in Vitamins Category.")

    # 6. Check /healthcare?category=Cold & Flu (Newly Added)
    log("Checking /healthcare?category=Cold & Flu...")
    resp = session.get(f"{BASE_URL}/healthcare", params={"category": "Cold & Flu"})
    if "Cetirizine 10mg" in resp.text:
         log("SUCCESS: Found 'Cetirizine 10mg' in Cold & Flu Category.")
    else:
         log("FAILURE: 'Cetirizine 10mg' NOT found in Cold & Flu Category.")

if __name__ == "__main__":
    try:
        test_category_view()
    except Exception as e:
        log(f"Exception: {e}")
