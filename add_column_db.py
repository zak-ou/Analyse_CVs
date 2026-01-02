import sqlite3

DB_NAME = "recruitment.db"

def add_column():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE offres ADD COLUMN nombre_postes INTEGER DEFAULT 1")
        print("Column 'nombre_postes' added successfully.")
    except sqlite3.OperationalError:
        print("Column 'nombre_postes' already exists.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_column()
