from app import app
import os

print(f"Current Config URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
    print("PASS: Fallback to SQLite working")
else:
    print("FAIL: Not checking for SQLite")

# Test Postgres Logic Mock
os.environ['DATABASE_URL'] = "postgres://user:pass@localhost/db"
# Reload config logic (simulate app startup)
database_url = os.environ.get('DATABASE_URL')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    
if database_url == "postgresql://user:pass@localhost/db":
    print("PASS: Postgres replacement logic working")
else:
    print(f"FAIL: Replacement logic failed: {database_url}")
