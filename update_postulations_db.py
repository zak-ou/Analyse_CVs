import sqlite3
import os

DB_NAME = "recruitment.db"

def update_schema():
    if not os.path.exists(DB_NAME):
        print(f"Database {DB_NAME} not found.")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        # Add 'statut' column
        try:
            c.execute("ALTER TABLE postulations ADD COLUMN statut TEXT DEFAULT 'En attente'")
            print("Added 'statut' column to 'postulations'.")
        except sqlite3.OperationalError:
            print("'statut' column might already exist.")

        # Add 'email_envoye' column
        try:
            c.execute("ALTER TABLE postulations ADD COLUMN email_envoye BOOLEAN DEFAULT 0")
            print("Added 'email_envoye' column to 'postulations'.")
        except sqlite3.OperationalError:
            print("'email_envoye' column might already exist.")

        conn.commit()
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_schema()
