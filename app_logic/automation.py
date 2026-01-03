import time
import threading
import database as db
from app_logic.email_service import EmailService
from app_logic.controller import RecruitmentController
import datetime
import os

# Global flag to track background worker
_worker_started = False

def _get_automation_controller():
    # Use internal caching for the heavy controller
    if not hasattr(_get_automation_controller, "controller"):
        _get_automation_controller.controller = RecruitmentController()
    return _get_automation_controller.controller

def start_background_worker(interval_seconds=60):
    """Starts a background thread that runs analysis periodically."""
    global _worker_started
    if _worker_started:
        return
    
    def worker_loop():
        print(f"🚀 background worker started (interval: {interval_seconds}s)")
        while True:
            try:
                run_pending_analyses()
            except Exception as e:
                print(f"❌ Error in background worker loop: {e}")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=worker_loop, daemon=True)
    thread.start()
    _worker_started = True

def run_pending_analyses():
    """
    Checks for offers where the deadline has passed.
    1. Triggers analysis automatically for unanalyzed apps.
    2. Performs candidate selection (Accepted/Refused) and sends emails.
    """
    try:
        # Get all offers - Fetch with recruiter info
        conn = db.sqlite3.connect(db.DB_NAME)
        conn.row_factory = db.sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT o.*, r.nom as r_nom, r.prenom as r_prenom, r.email as r_email 
            FROM offres o 
            JOIN recruteurs r ON o.recruteur_id = r.id
        """)
        all_jobs = c.fetchall()
        
        controller = _get_automation_controller()
        email_service = EmailService()
        
        for job in all_jobs:
            # Check if deadline passed
            deadline_str = str(job['date_limite'])
            try:
                if len(deadline_str) > 10:
                     deadline_dt = datetime.datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
                     is_past = datetime.datetime.now() > deadline_dt
                else:
                     deadline_dt = datetime.datetime.strptime(deadline_str, "%Y-%m-%d")
                     is_past = datetime.date.today() > deadline_dt.date()
                
                if is_past and not job['notifications_envoyees']:
                    # PHASE 1: ANALYSIS (for those not yet analyzed)
                    apps = db.get_postulations_for_offer(job['id'])
                    unanalyzed = [app for app in apps if app['score'] is None and app['cv_url']]
                    
                    if unanalyzed:
                        print(f"Auto-Analyzing {len(unanalyzed)} applications for expired job: {job['titre']}")
                        required_skills = [s.strip() for s in job['competences_requises'].split(',') if s.strip()]
                        
                        class FileWrapper:
                             def __init__(self, path):
                                 self.name = os.path.basename(path)
                                 self.path = path
                             def getbuffer(self):
                                 with open(self.path, "rb") as f:
                                     return f.read()

                        files_to_process = []
                        app_map = {}
                        for app in unanalyzed:
                             f_path = app['cv_url']
                             if f_path and os.path.exists(f_path):
                                 wrapper = FileWrapper(f_path)
                                 files_to_process.append(wrapper)
                                 app_map[wrapper.name] = app['id']
                        
                        if files_to_process:
                             results = controller.process_uploads(files_to_process, required_skills)
                             for res in results:
                                 if res['filename'] in app_map:
                                     db.update_postulation_results(app_map[res['filename']], res['score'], res)
                        print("Auto-analysis complete.")
                    
                    # RE-FETCH to get newly analyzed scores
                    apps = db.get_postulations_for_offer(job['id'])
                    
                    # PHASE 2: SELECTION
                    scored_apps = [a for a in apps if a['score'] is not None]
                    scored_apps.sort(key=lambda x: x['score'], reverse=True)
                    
                    nb_postes = job['nombre_postes'] if job['nombre_postes'] else 1
                    
                    selected = scored_apps[:nb_postes]
                    refused = scored_apps[nb_postes:]
                    
                    # Process Selected
                    for cand in selected:
                        needs_status_update = cand['statut_postulation'] != "Accepted"
                        needs_email = not cand['email_envoye']
                        
                        if needs_status_update or needs_email:
                            print(f"Assigning 'Accepted' to {cand['nom']} for job {job['titre']}")
                            if needs_status_update:
                                db.update_postulation_status(cand['id'], "Accepted", email_envoye=False)
                            
                            sent = email_service.send_acceptance_email(cand['email'], f"{cand['prenom']} {cand['nom']}", job['titre'])
                            if sent:
                                db.update_postulation_status(cand['id'], "Accepted", email_envoye=True)

                    # Process Refused
                    for cand in refused:
                        needs_status_update = cand['statut_postulation'] != "Refused"
                        needs_email = not cand['email_envoye']
                        
                        if needs_status_update or needs_email:
                            print(f"Assigning 'Refused' to {cand['nom']} for job {job['titre']}")
                            if needs_status_update:
                                db.update_postulation_status(cand['id'], "Refused", email_envoye=False)
                                
                            sent = email_service.send_refusal_email(cand['email'], f"{cand['prenom']} {cand['nom']}", job['titre'])
                            if sent:
                                db.update_postulation_status(cand['id'], "Refused", email_envoye=True)
                    
                    # PHASE 3: NOTIFY RECRUITER
                    email_service.send_offer_closed_email_to_recruiter(
                        job['r_email'],
                        f"{job['r_prenom']} {job['r_nom']}",
                        job['titre'],
                        len(apps)
                    )
                    # Mark offer as notified
                    db.set_offer_notified(job['id'])
                    print(f"Offer {job['titre']} processed and recruiter notified.")
                            
            except ValueError:
                continue 

        conn.close()

    except Exception as e:
        print(f"Error in auto-analysis/selection: {e}")
