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
    
    _worker_started = True 
    
    def worker_loop():
        # Small delay to ensure DB and app are ready
        time.sleep(5)
        print(f"🚀 [BACKGROUND] Automation worker started (Interval: {interval_seconds}s)")
        while True:
            try:
                run_pending_analyses()
            except Exception as e:
                print(f"❌ [BACKGROUND] Error in loop: {e}")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=worker_loop, name="AutomationWorker", daemon=True)
    thread.start()
    print(f"📡 [SYSTEM] Background thread '{thread.name}' dispatched.")

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
            WHERE o.notifications_envoyees = 0
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
                
                is_closed_manually = job['statut'] == 'clôturé'
                if (is_past or is_closed_manually) and not job['notifications_envoyees']:
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
                    
                    # PHASE 2: SELECTION (All candidates must have a result)
                    scored_apps = []
                    for a in apps:
                        # If analysis failed or hasn't run, score is effectively 0 for selection
                        score_val = a['score'] if a['score'] is not None else 0
                        scored_apps.append({'data': a, 'score': score_val})
                        
                    # Sort candidates by score
                    scored_apps.sort(key=lambda x: x['score'], reverse=True)
                    
                    nb_postes = job['nombre_postes'] if job['nombre_postes'] else 1
                    
                    selected = scored_apps[:nb_postes]
                    refused = scored_apps[nb_postes:]
                    
                    # Mark offer as notified immediately to avoid infinite retry loops if emails fail
                    db.set_offer_notified(job['id'])
                    
                    # 1. Process Selected
                    for entry in selected:
                        cand = entry['data']
                        needs_status_update = cand['statut_postulation'] != "Accepted"
                        needs_email = not cand['email_envoye']
                        
                        if needs_status_update or needs_email:
                            if needs_status_update:
                                db.update_postulation_status(cand['id'], "Accepted", email_envoye=False)
                            
                            # Simple validation: must contain @
                            if "@" in str(cand['email']):
                                sent = email_service.send_acceptance_email(cand['email'], f"{cand['prenom']} {cand['nom']}", job['titre'])
                                if sent:
                                    db.update_postulation_status(cand['id'], "Accepted", email_envoye=True)
                            else:
                                print(f"⚠️ Skipping email for invalid address: {cand['email']}")
                                # Mark as 'sent' anyway to avoid retrying junk data
                                db.update_postulation_status(cand['id'], "Accepted", email_envoye=True)

                    # 2. Process Refused
                    for entry in refused:
                        cand = entry['data']
                        needs_status_update = cand['statut_postulation'] != "Refused"
                        needs_email = not cand['email_envoye']
                        
                        if needs_status_update or needs_email:
                            if needs_status_update:
                                db.update_postulation_status(cand['id'], "Refused", email_envoye=False)
                            
                            if "@" in str(cand['email']):
                                sent = email_service.send_refusal_email(cand['email'], f"{cand['prenom']} {cand['nom']}", job['titre'])
                                if sent:
                                    db.update_postulation_status(cand['id'], "Refused", email_envoye=True)
                            else:
                                print(f"⚠️ Skipping email for invalid address: {cand['email']}")
                                db.update_postulation_status(cand['id'], "Refused", email_envoye=True)
                    
                    # PHASE 3: NOTIFY RECRUITER WITH STATS
                    total_apps = len(apps)
                    avg_score = sum(x['score'] for x in scored_apps) / total_apps if total_apps > 0 else 0
                    
                    stats = {
                        'total': total_apps,
                        'accepted': len(selected),
                        'refused': len(refused),
                        'avg_score': avg_score
                    }
                    
                    if "@" in str(job['r_email']):
                        email_service.send_offer_closed_email_to_recruiter(
                            job['r_email'],
                            f"{job['r_prenom']} {job['r_nom']}",
                            job['titre'],
                            stats
                        )
                    
                    print(f"✅ Offer '{job['titre']}' fully processed (notifications attempted).")

                            
            except ValueError:
                continue 

        conn.close()

    except Exception as e:
        print(f"Error in auto-analysis/selection: {e}")
