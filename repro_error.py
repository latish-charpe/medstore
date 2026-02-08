import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

s = requests.Session()

# 1. Login
login_payload = {
    "username": "admin",
    "password": "admin123"
}
print(f"Logging in as {login_payload['username']}...")
r = s.post(f"{BASE_URL}/login", data=login_payload)
print(f"Login Status: {r.status_code}")
if "Invalid username" in r.text:
    print("Login failed!")
    sys.exit(1)

# 2. Access /medicines
print("Accessing /medicines...")
r = s.get(f"{BASE_URL}/medicines")
print(f"Status: {r.status_code}")
if r.status_code == 500:
    print("ERROR FOUND:")
    print(r.text) # Should contain traceback if debug=True
else:
    print("Page load success.")

# 3. Access /healthcare
print("Accessing /healthcare...")
r = s.get(f"{BASE_URL}/healthcare")
print(f"Status: {r.status_code}")
if r.status_code == 500:
    print("ERROR FOUND:")
    print(r.text)

# 4. Access /dashboard
print("Accessing /dashboard...")
r = s.get(f"{BASE_URL}/dashboard")
print(f"Status: {r.status_code}")
if r.status_code == 500:
    print("ERROR FOUND:")
    print(r.text)
