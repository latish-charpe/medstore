import sqlite3
import os

def add_store_id_column():
    db_path = os.path.join(os.path.dirname(__file__), 'medstore.db')
    print(f"Connecting to database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("SELECT store_id FROM user LIMIT 1")
        print("Column 'store_id' already exists.")
    except sqlite3.OperationalError:
        print("Adding 'store_id' column to User table...")
        try:
            # Add column 'store_id' with default 'medstore_main'
            cursor.execute("ALTER TABLE user ADD COLUMN store_id VARCHAR(50) DEFAULT 'medstore_main'")
            conn.commit()
            print("Successfully added 'store_id' column.")
        except Exception as e:
            print(f"Error adding column: {e}")
            conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_store_id_column()

