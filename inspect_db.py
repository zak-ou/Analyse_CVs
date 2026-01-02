import sqlite3

try:
    conn = sqlite3.connect("recruitment.db")
    c = conn.cursor()
    c.execute("PRAGMA table_info(postulations)")
    columns = c.fetchall()
    print("Columns in 'postulations':")
    for col in columns:
        print(col)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
