import sqlite3

DB_NAME = "recruitment.db"

def migrate_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        print("Starting migration...")

        # 1. Rename existing table
        print("Renaming old table...")
        c.execute("ALTER TABLE postulations RENAME TO postulations_old")

        # 2. Create new table with correct schema (including id)
        print("Creating new table...")
        c.execute('''CREATE TABLE postulations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        candidat_id INTEGER,
                        offre_id INTEGER,
                        date_postulation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        cv_url TEXT,
                        donnees_analysees TEXT,
                        score Real,
                        FOREIGN KEY (candidat_id) REFERENCES candidats (id),
                        FOREIGN KEY (offre_id) REFERENCES offres (id)
                    )''')

        # 3. Copy data
        print("Copying data...")
        # We explicitly list columns to copy to avoid mismatches
        c.execute('''INSERT INTO postulations (candidat_id, offre_id, date_postulation, cv_url, donnees_analysees, score)
                     SELECT candidat_id, offre_id, date_postulation, cv_url, donnees_analysees, score 
                     FROM postulations_old''')

        # 4. Drop old table
        print("Dropping old table...")
        c.execute("DROP TABLE postulations_old")

        conn.commit()
        print("Migration successful! 'postulations' table now has an 'id' column.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
