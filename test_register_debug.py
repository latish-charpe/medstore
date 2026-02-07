import requests
import hashlib
import sys

BASE_URL = "http://127.0.0.1:5000"
CODE = "medstore2026"

def log(msg):
    with open("debug_result.txt", "a") as f:
        f.write(msg + "\n")
    print(msg)

def test_register():
    # Clear log
    with open("debug_result.txt", "w") as f:
        f.write("Starting Test...\n")

    # 1. Calculate Hash locally to verify what it SHOULD be
    expected_hash = hashlib.sha256(CODE.encode()).hexdigest()
    log(f"Client-calculated Hash for '{CODE}': {expected_hash}")

    # 2. Attempt Registration
    payload = {
        "username": "debug_manager_v2",
        "password": "password123",
        "confirm_password": "password123",
        "secret_code": CODE
    }
    
    try:
        session = requests.Session()
        log(f"Attempting register with code: {CODE}")
        response = session.post(f"{BASE_URL}/register", data=payload, allow_redirects=False)
        
        log(f"Response Status: {response.status_code}")
        if response.status_code == 302:
            log("Registration SUCCESS (Redirected to login)")
        else:
            log("Registration FAILED")
            if "Invalid Admin Secret Code" in response.text:
                log("Error: Invalid Admin Secret Code detected in response.")
            else:
                log("Error: Unknown failure.")
                # log(response.text[:500])
                
    except Exception as e:
        log(f"Connection Failed: {e}")

if __name__ == "__main__":
    test_register()
