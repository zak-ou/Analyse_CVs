import sqlite3
import os

DB_NAME = "recruitment.db"

def test_insert():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        # Check if we can insert a dummy (or at least check schema)
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='postulations'")
        if not c.fetchone():
            print("Table postulations does not exist!")
            return
        
        print("Table postulations exists.")
        
        # Test a dry run of an insert if possible, or just check columns
        c.execute("PRAGMA table_info(postulations)")
        cols = c.fetchall()
        print(f"Columns: {cols}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_insert()
