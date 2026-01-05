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
                    nombre_postes INTEGER DEFAULT 1,
                    notifications_envoyees INTEGER DEFAULT 0,
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
                    statut TEXT DEFAULT 'Pending',
                    email_envoye INTEGER DEFAULT 0,
                    FOREIGN KEY (candidat_id) REFERENCES candidats (id),
                    FOREIGN KEY (offre_id) REFERENCES offres (id)
                )''')
    
    # 5. CV Data Tables
    c.execute('''CREATE TABLE IF NOT EXISTS cv_coordonnees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidat_id INTEGER UNIQUE,
                    nom_complet TEXT,
                    email TEXT,
                    telephone TEXT,
                    ville_region TEXT,
                    profil TEXT,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (candidat_id) REFERENCES candidats (id)
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS cv_education (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidat_id INTEGER,
                    etablissement TEXT,
                    diplome TEXT,
                    periode TEXT,
                    details TEXT,
                    ordre INTEGER DEFAULT 0,
                    FOREIGN KEY (candidat_id) REFERENCES candidats (id)
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS cv_experience (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidat_id INTEGER,
                    entreprise TEXT,
                    titre_mission TEXT,
                    periode TEXT,
                    realisations TEXT,
                    ordre INTEGER DEFAULT 0,
                    FOREIGN KEY (candidat_id) REFERENCES candidats (id)
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS cv_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidat_id INTEGER UNIQUE,
                    languages TEXT,
                    technologies TEXT,
                    databases TEXT,
                    tools TEXT,
                    networking TEXT,
                    soft_skills TEXT,
                    FOREIGN KEY (candidat_id) REFERENCES candidats (id)
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS cv_langues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidat_id INTEGER,
                    langue TEXT,
                    niveau TEXT,
                    ordre INTEGER DEFAULT 0,
                    FOREIGN KEY (candidat_id) REFERENCES candidats (id)
                )''')
    
    # Check for missing columns and add them (Migration)
    try:
        c.execute("ALTER TABLE offres ADD COLUMN nombre_postes INTEGER DEFAULT 1")
    except: pass
    try:
        c.execute("ALTER TABLE offres ADD COLUMN notifications_envoyees INTEGER DEFAULT 0")
    except: pass
    try:
        c.execute("ALTER TABLE postulations ADD COLUMN statut TEXT DEFAULT 'Pending'")
    except: pass
    try:
        c.execute("ALTER TABLE postulations ADD COLUMN email_envoye INTEGER DEFAULT 0")
    except: pass

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
        # Les candidats ne voient que les offres actives ET dont le délai n'est pas passé
        c.execute("SELECT * FROM offres WHERE statut = 'actif' AND datetime(date_limite) >= datetime('now', 'localtime')")
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

def get_market_offers():
    """Fetches all active offers with recruiter details for the market news feed."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # On ne montre que ce qui est actif et non expiré
    c.execute('''SELECT o.*, r.nom as recruteur_nom, r.prenom as recruteur_prenom, r.domaine as recruteur_domaine 
                 FROM offres o 
                 JOIN recruteurs r ON o.recruteur_id = r.id 
                 WHERE o.statut = 'actif' AND datetime(o.date_limite) >= datetime('now', 'localtime')
                 ORDER BY o.id DESC''')
    offers = c.fetchall()
    conn.close()
    return offers

def set_offer_notified(offer_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE offres SET notifications_envoyees = 1 WHERE id = ?", (offer_id,))
    conn.commit()
    conn.close()

def delete_offer(offer_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM offres WHERE id = ?", (offer_id,))
    conn.commit()
    conn.close()

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
    
    try:
        c.execute('''INSERT INTO postulations (offre_id, candidat_id, cv_url, statut) 
                     VALUES (?, ?, ?, 'Pending')''', (offre_id, candidat_id, cv_url))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error submitting postulation: {e}")
        return False
    finally:
        conn.close()
        
def update_postulation(offre_id, candidat_id, cv_url):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Reset score and analyzed data when CV is updated
    c.execute("""UPDATE postulations 
                 SET cv_url = ?, score = NULL, donnees_analysees = NULL, statut = 'Pending', email_envoye = 0, date_postulation = CURRENT_TIMESTAMP
                 WHERE offre_id = ? AND candidat_id = ?""", 
              (cv_url, offre_id, candidat_id))
    conn.commit()
    conn.close()
    return True

def get_postulations_for_offer(offre_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Join with candidats to get name
    c.execute('''SELECT p.*, c.nom as nom, c.prenom as prenom, c.email as email, p.statut as statut_postulation
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
    # Collision warning: p.statut and o.statut. 
    # We alias o.statut to statut_offre. p.statut is inside p.* (as statut currently? Or need to alias?)
    # Safest is to explicitly select key columns or alias o.statut.
    c.execute('''SELECT p.*, o.titre, o.statut as statut_offre, o.date_limite, p.statut as statut_postulation
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

def update_postulation_status(postulation_id, statut, email_envoye=False):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE postulations SET statut = ?, email_envoye = ? WHERE id = ?", (statut, email_envoye, postulation_id))
    conn.commit()
    conn.close()

# --- CV Data Management ---

def save_cv_coordonnees(candidat_id, nom_complet, email, telephone, ville_region, profil):
    """Save or update candidate's CV contact information and profile."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        # Check if exists
        c.execute("SELECT id FROM cv_coordonnees WHERE candidat_id = ?", (candidat_id,))
        if c.fetchone():
            c.execute("""UPDATE cv_coordonnees 
                        SET nom_complet=?, email=?, telephone=?, ville_region=?, profil=?, date_modification=CURRENT_TIMESTAMP
                        WHERE candidat_id=?""", 
                     (nom_complet, email, telephone, ville_region, profil, candidat_id))
        else:
            c.execute("""INSERT INTO cv_coordonnees (candidat_id, nom_complet, email, telephone, ville_region, profil)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                     (candidat_id, nom_complet, email, telephone, ville_region, profil))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving CV coordonnees: {e}")
        return False
    finally:
        conn.close()

def get_cv_coordonnees(candidat_id):
    """Get candidate's CV contact information."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM cv_coordonnees WHERE candidat_id = ?", (candidat_id,))
    data = c.fetchone()
    conn.close()
    return data

def save_cv_education(candidat_id, education_list):
    """Save education entries. education_list is a list of dicts with keys: etablissement, diplome, periode, details."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        # Delete existing
        c.execute("DELETE FROM cv_education WHERE candidat_id = ?", (candidat_id,))
        # Insert new
        for i, edu in enumerate(education_list):
            c.execute("""INSERT INTO cv_education (candidat_id, etablissement, diplome, periode, details, ordre)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                     (candidat_id, edu.get('etablissement', ''), edu.get('diplome', ''), 
                      edu.get('periode', ''), edu.get('details', ''), i))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving education: {e}")
        return False
    finally:
        conn.close()

def get_cv_education(candidat_id):
    """Get candidate's education entries."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM cv_education WHERE candidat_id = ? ORDER BY ordre", (candidat_id,))
    data = c.fetchall()
    conn.close()
    return data

def save_cv_experience(candidat_id, experience_list):
    """Save experience entries."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM cv_experience WHERE candidat_id = ?", (candidat_id,))
        for i, exp in enumerate(experience_list):
            c.execute("""INSERT INTO cv_experience (candidat_id, entreprise, titre_mission, periode, realisations, ordre)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                     (candidat_id, exp.get('entreprise', ''), exp.get('titre_mission', ''), 
                      exp.get('periode', ''), exp.get('realisations', ''), i))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving experience: {e}")
        return False
    finally:
        conn.close()

def get_cv_experience(candidat_id):
    """Get candidate's experience entries."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM cv_experience WHERE candidat_id = ? ORDER BY ordre", (candidat_id,))
    data = c.fetchall()
    conn.close()
    return data

def save_cv_skills(candidat_id, languages, technologies, databases, tools, networking, soft_skills):
    """Save technical and soft skills."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM cv_skills WHERE candidat_id = ?", (candidat_id,))
        if c.fetchone():
            c.execute("""UPDATE cv_skills 
                        SET languages=?, technologies=?, databases=?, tools=?, networking=?, soft_skills=?
                        WHERE candidat_id=?""",
                     (languages, technologies, databases, tools, networking, soft_skills, candidat_id))
        else:
            c.execute("""INSERT INTO cv_skills (candidat_id, languages, technologies, databases, tools, networking, soft_skills)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                     (candidat_id, languages, technologies, databases, tools, networking, soft_skills))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving skills: {e}")
        return False
    finally:
        conn.close()

def get_cv_skills(candidat_id):
    """Get candidate's skills."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM cv_skills WHERE candidat_id = ?", (candidat_id,))
    data = c.fetchone()
    conn.close()
    return data

def save_cv_langues(candidat_id, langues_list):
    """Save language entries."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM cv_langues WHERE candidat_id = ?", (candidat_id,))
        for i, lang in enumerate(langues_list):
            c.execute("""INSERT INTO cv_langues (candidat_id, langue, niveau, ordre)
                        VALUES (?, ?, ?, ?)""",
                     (candidat_id, lang.get('langue', ''), lang.get('niveau', ''), i))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving languages: {e}")
        return False
    finally:
        conn.close()

def get_cv_langues(candidat_id):
    """Get candidate's languages."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM cv_langues WHERE candidat_id = ? ORDER BY ordre", (candidat_id,))
    data = c.fetchall()
    conn.close()
    return data

def get_complete_cv_data(candidat_id):
    """Get all CV data for a candidate."""
    return {
        'coordonnees': get_cv_coordonnees(candidat_id),
        'education': get_cv_education(candidat_id),
        'experience': get_cv_experience(candidat_id),
        'skills': get_cv_skills(candidat_id),
        'langues': get_cv_langues(candidat_id)
    }

