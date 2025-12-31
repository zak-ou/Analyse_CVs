import sqlite3
import hashlib

DB_NAME = "recruitment.db"

def init_db():
    """Initializes the database with necessary tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Candidates table (users)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')

    # Recruiters table (recreteur)
    c.execute('''CREATE TABLE IF NOT EXISTS recreteur (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')

    # Jobs table
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    skills_required TEXT,
                    experience_min INTEGER,
                    deadline DATE,
                    status TEXT DEFAULT 'actif',
                    recruiter_id INTEGER,
                    FOREIGN KEY (recruiter_id) REFERENCES recreteur (id)
                )''')

    # Applications table
    c.execute('''CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER,
                    candidate_id INTEGER,
                    cv_filepath TEXT,
                    upload_date DATE DEFAULT CURRENT_DATE,
                    score REAL,
                    FOREIGN KEY (job_id) REFERENCES jobs (id),
                    FOREIGN KEY (candidate_id) REFERENCES users (id)
                )''')
    
    conn.commit()
    conn.close()

def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- User Management ---

def create_user(username, password, table='users'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed = _hash_password(password)
    try:
        c.execute(f"INSERT INTO {table} (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password, table='users'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed = _hash_password(password)
    c.execute(f"SELECT id, username FROM {table} WHERE username = ? AND password = ?", (username, hashed))
    user = c.fetchone()
    conn.close()
    return user # Returns (id, username) or None

# --- Job Management ---

def create_job(title, description, skills, exp_min, deadline, recruiter_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO jobs (title, description, skills_required, experience_min, deadline, status, recruiter_id)
                 VALUES (?, ?, ?, ?, ?, 'actif', ?)''', 
              (title, description, skills, exp_min, deadline, recruiter_id))
    conn.commit()
    conn.close()

def get_jobs(recruiter_id=None):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if recruiter_id:
        c.execute("SELECT * FROM jobs WHERE recruiter_id = ?", (recruiter_id,))
    else:
        # Candidates see only active jobs
        c.execute("SELECT * FROM jobs WHERE status = 'actif'")
    jobs = c.fetchall()
    conn.close()
    return jobs

def get_job_by_id(job_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    job = c.fetchone()
    conn.close()
    return job

# --- Application Management ---

def submit_application(job_id, candidate_id, cv_filepath):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Check if already applied
    c.execute("SELECT id FROM applications WHERE job_id = ? AND candidate_id = ?", (job_id, candidate_id))
    if c.fetchone():
        conn.close()
        return False # Already applied
        
    c.execute("INSERT INTO applications (job_id, candidate_id, cv_filepath, score) VALUES (?, ?, ?, NULL)",
              (job_id, candidate_id, cv_filepath))
    conn.commit()
    conn.close()
    return True

def get_applications_for_job(job_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Join with users to get candidate name (assuming 'username' is name for now)
    c.execute('''SELECT app.*, u.username as candidate_name 
                 FROM applications app 
                 JOIN users u ON app.candidate_id = u.id 
                 WHERE app.job_id = ?''', (job_id,))
    apps = c.fetchall()
    conn.close()
    return apps

def get_applications_for_candidate(candidate_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Join with jobs to get job title and status
    c.execute('''SELECT app.*, j.title as job_title, j.status as job_status, j.deadline
                 FROM applications app 
                 JOIN jobs j ON app.job_id = j.id 
                 WHERE app.candidate_id = ?''', (candidate_id,))
    apps = c.fetchall()
    conn.close()
    return apps

def update_application_results(app_id, score, skills):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Convert list to string if needed
    if isinstance(skills, list):
        skills_str = ", ".join(skills)
    else:
        skills_str = str(skills)
    
    c.execute("UPDATE applications SET score = ?, skills = ? WHERE id = ?", (score, skills_str, app_id))
    conn.commit()
    conn.close()

def update_job_status(job_id, status):
    """Updates the status of a job (e.g. 'actif' or 'closed')."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
    conn.commit()
    conn.close()
