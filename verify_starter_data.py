import requests
import time

BASE_URL = "http://127.0.0.1:5000"
CODE = "medstore2026"
USERNAME = f"store_{int(time.time())}" # Unique user

def log(msg):
    with open("verify_result.txt", "a") as f:
        f.write(msg + "\n")
    print(msg)

def test_flow():
    with open("verify_result.txt", "w") as f:
        f.write("Starting Verification...\n")
        
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
    if resp.status_code != 200: # Should redirect or show success
        log(f"Registration status: {resp.status_code}")
    
    # 2. Login
    log("Logging in...")
    login_payload = {
        "username": USERNAME,
        "password": "password123"
    }
    resp = session.post(f"{BASE_URL}/login", data=login_payload)
    
    if "Dashboard" in resp.text:
        log("Login Successful! Dashboard loaded.")
        
        # 3. Check for Starter Medicines
        if "Paracetamol 650" in resp.text:
            log("SUCCESS: 'Paracetamol 650' found in dashboard.")
        else:
            log("FAILURE: Starter medicines NOT found.")
            # log(resp.text[:500])
            
        if "Volini Gel" in resp.text:
            log("SUCCESS: 'Volini Gel' found.")
            
    else:
        log("Login Failed or Dashboard not reached.")
        if "sqlalchemy.exc" in resp.text:
             log("DB SCHEMA ERROR DETECTED")

if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        log(f"Exception: {e}")
