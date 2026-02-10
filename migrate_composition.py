import sqlite3
import os

db_path = 'medstore.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE medicine ADD COLUMN composition TEXT')
        print("Column 'composition' added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'composition' already exists.")
        else:
            print(f"Error: {e}")
    conn.commit()
    conn.close()
else:
    print("Database file not found.")
