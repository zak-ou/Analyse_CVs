import sqlite3

DB_NAME = "recruitment.db"

def list_tables():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    for table in tables:
        print(f"\nColumns in '{table[0]}':")
        c.execute(f"PRAGMA table_info({table[0]})")
        for col in c.fetchall():
            print(col)
    conn.close()

if __name__ == "__main__":
    list_tables()
