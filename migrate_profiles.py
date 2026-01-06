import sqlite3

DB_NAME = "recruitment.db"

def migrate():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Candidats columns
    columns_candidats = [
        ('photo_url', 'TEXT'),
        ('bio', 'TEXT'),
        ('linkedin_url', 'TEXT'),
        ('github_url', 'TEXT'),
        ('portfolio_url', 'TEXT')
    ]
    
    for col_name, col_type in columns_candidats:
        try:
            c.execute(f"ALTER TABLE candidats ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name} to candidats")
        except sqlite3.OperationalError:
            print(f"Column {col_name} already exists in candidats")

    # 2. Recruteurs columns
    columns_recruteurs = [
        ('photo_url', 'TEXT'),
        ('entreprise_nom', 'TEXT'),
        ('entreprise_site', 'TEXT'),
        ('entreprise_description', 'TEXT')
    ]
    
    for col_name, col_type in columns_recruteurs:
        try:
            c.execute(f"ALTER TABLE recruteurs ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name} to recruteurs")
        except sqlite3.OperationalError:
            print(f"Column {col_name} already exists in recruteurs")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
