import sqlite3
import os

def add_order_address_columns():
    db_path = os.path.join(os.path.dirname(__file__), 'medstore.db')
    print(f"Connecting to database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    columns = [
        ("full_name", "VARCHAR(100)"),
        ("mobile_number", "VARCHAR(15)"),
        ("address_line1", "VARCHAR(200)"),
        ("area_landmark", "VARCHAR(100)"),
        ("city", "VARCHAR(50)"),
        ("state", "VARCHAR(50)"),
        ("pincode", "VARCHAR(10)")
    ]

    try:
        for col_name, col_type in columns:
            try:
                cursor.execute(f"SELECT {col_name} FROM \"order\" LIMIT 1")
                print(f"Column '{col_name}' already exists.")
            except sqlite3.OperationalError:
                print(f"Adding '{col_name}' column to Order table...")
                cursor.execute(f"ALTER TABLE \"order\" ADD COLUMN {col_name} {col_type}")
                print(f"Successfully added '{col_name}'.")
        
        conn.commit()
    except Exception as e:
        print(f"Error adding columns: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_order_address_columns()
