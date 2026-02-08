import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_user(username, password, role_name):
    print(f"\n--- Testing as {role_name} ({username}) ---")
    s = requests.Session()
    
    # Login
    r = s.post(f"{BASE_URL}/login", data={"username": username, "password": password})
    if r.status_code != 200 or "Invalid" in r.text:
        print("Login failed")
        return

    endpoints = [
        "/", 
        "/about", 
        "/medicines", 
        "/healthcare", 
        "/cart", 
        "/checkout",
        "/symptom-checker"
    ]
    
    if role_name == "Manager":
        endpoints.append("/dashboard")

    for ep in endpoints:
        print(f"Checking {ep}...", end=" ")
        try:
            r = s.get(f"{BASE_URL}{ep}")
            print(f"{r.status_code}")
            if r.status_code == 500:
                print("!!! ERROR 500 FOUND !!!")
                print(r.text[:500]) # First 500 chars
        except Exception as e:
            print(f"Exception: {e}")

# Test Admin (Manager)
test_user("admin", "admin123", "Manager")

# Test Customer (Create one first)
s_reg = requests.Session()
reg_data = {
    "name": "Test Customer",
    "username": "customer99",
    "password": "password123",
    "confirm_password": "password123"
}
s_reg.post(f"{BASE_URL}/register", data=reg_data)
test_user("customer99", "password123", "Customer")
