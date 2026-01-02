import sqlite3
import hashlib
import json

DB_NAME = "recruitment.db"

def init_db():
    """Initializes the database with new schema (French tables)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Candidats (replacing users)
    c.execute('''CREATE TABLE IF NOT EXISTS candidats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    age INTEGER,
                    email TEXT UNIQUE NOT NULL,
                    num_tele TEXT,
                    mot_de_passe TEXT NOT NULL,
                    niveau_diplome TEXT
                )''')

    # 2. Recruteurs (replacing recreteur)
    c.execute('''CREATE TABLE IF NOT EXISTS recruteurs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    domaine TEXT,
                    email TEXT UNIQUE NOT NULL,
                    num_tele TEXT,
                    mot_de_passe TEXT NOT NULL
                )''')

    # 3. Offres (Jobs)
    c.execute('''CREATE TABLE IF NOT EXISTS offres (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titre TEXT NOT NULL,
                    domaine TEXT,
                    competences_requises TEXT,
                    recruteur_id INTEGER,
                    description TEXT,
                    experience_min INTEGER,
                    date_limite DATE,
                    statut TEXT DEFAULT 'actif',
                    FOREIGN KEY (recruteur_id) REFERENCES recruteurs (id)
                )''')

    # 4. Postulations (Applications)
    c.execute('''CREATE TABLE IF NOT EXISTS postulations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidat_id INTEGER,
                    offre_id INTEGER,
                    date_postulation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cv_url TEXT,
                    donnees_analysees TEXT, -- Stored as JSON
                    score Real,
                    FOREIGN KEY (candidat_id) REFERENCES candidats (id),
                    FOREIGN KEY (offre_id) REFERENCES offres (id)
                )''')
    
    conn.commit()
    conn.close()

def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- User Management (Generic for both tables) ---

def create_user(nom, prenom, email, password, role, **kwargs):
    """
    Creates a user in either 'candidats' or 'recruteurs'.
    kwargs can contain: age, num_tele, niveau_diplome, domaine
    """
    table = 'recruteurs' if role == 'Recruteur' else 'candidats'
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed = _hash_password(password)
    
    try:
        if table == 'recruteurs':
            c.execute('''INSERT INTO recruteurs (nom, prenom, domaine, email, num_tele, mot_de_passe) 
                         VALUES (?, ?, ?, ?, ?, ?)''', 
                      (nom, prenom, kwargs.get('domaine'), email, kwargs.get('num_tele'), hashed))
        else:
            c.execute('''INSERT INTO candidats (nom, prenom, age, email, num_tele, mot_de_passe, niveau_diplome) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                      (nom, prenom, kwargs.get('age'), email, kwargs.get('num_tele'), hashed, kwargs.get('niveau_diplome')))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        conn.close()

def verify_user(email, password, role):
    table = 'recruteurs' if role == 'Recruteur' else 'candidats'
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    hashed = _hash_password(password)
    c.execute(f"SELECT * FROM {table} WHERE email = ? AND mot_de_passe = ?", (email, hashed))
    user = c.fetchone()
    conn.close()
    return user # Returns Row object or None

# --- Job Management (Offres) ---

def create_offer(titre, description, competences, exp_min, date_limite, recruteur_id, domaine, nombre_postes=1):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO offres (titre, description, competences_requises, experience_min, date_limite, statut, recruteur_id, domaine, nombre_postes)
                 VALUES (?, ?, ?, ?, ?, 'actif', ?, ?, ?)''', 
              (titre, description, competences, exp_min, date_limite, recruteur_id, domaine, nombre_postes))
    conn.commit()
    conn.close()

def get_offers(recruteur_id=None):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if recruteur_id:
        c.execute("SELECT * FROM offres WHERE recruteur_id = ?", (recruteur_id,))
    else:
        # Les candidats ne voient que les offres actives
        c.execute("SELECT * FROM offres WHERE statut = 'actif'")
    jobs = c.fetchall()
    conn.close()
    return jobs

def get_offer_by_id(offer_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM offres WHERE id = ?", (offer_id,))
    job = c.fetchone()
    conn.close()
    return job

def update_offer(offer_id, titre, description, competences, exp_min, date_limite, domaine, statut, nombre_postes):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''UPDATE offres 
                 SET titre=?, description=?, competences_requises=?, experience_min=?, date_limite=?, domaine=?, statut=?, nombre_postes=?
                 WHERE id=?''', 
              (titre, description, competences, exp_min, date_limite, domaine, statut, nombre_postes, offer_id))
    conn.commit()
    conn.close()

# --- Application Management (Postulations) ---

def submit_postulation(offre_id, candidat_id, cv_url):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Check if already applied
    c.execute("SELECT id FROM postulations WHERE offre_id = ? AND candidat_id = ?", (offre_id, candidat_id))
    if c.fetchone():
        conn.close()
        return False # Already applied
        
    c.execute("INSERT INTO postulations (offre_id, candidat_id, cv_url, score) VALUES (?, ?, ?, NULL)",
              (offre_id, candidat_id, cv_url))
    conn.commit()
    conn.close()
    return True

def get_postulations_for_offer(offre_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Join with candidats to get name
    c.execute('''SELECT p.*, c.nom, c.prenom, c.email
                 FROM postulations p 
                 JOIN candidats c ON p.candidat_id = c.id 
                 WHERE p.offre_id = ?''', (offre_id,))
    apps = c.fetchall()
    conn.close()
    return apps

def get_postulations_for_candidate(candidat_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Join with offres to get title and status
    c.execute('''SELECT p.*, o.titre, o.statut, o.date_limite
                 FROM postulations p 
                 JOIN offres o ON p.offre_id = o.id 
                 WHERE p.candidat_id = ?''', (candidat_id,))
    apps = c.fetchall()
    conn.close()
    return apps

def update_postulation_results(postulation_id, score, analysis_json):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # analysis_json should be a dict or json string
    if isinstance(analysis_json, dict):
        analysis_str = json.dumps(analysis_json)
    else:
        analysis_str = str(analysis_json)
    
    c.execute("UPDATE postulations SET score = ?, donnees_analysees = ? WHERE id = ?", (score, analysis_str, postulation_id))
    conn.commit()
    conn.close()
