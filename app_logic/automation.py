import database as db
from app_logic.controller import RecruitmentController
import datetime
import os
import json

def run_pending_analyses():
    """
    Checks for offers where the deadline has passed but some applications remain unanalyzed.
    Triggers analysis automatically.
    """
    try:
        # Get all offers
        jobs = db.get_offers(recruteur_id=None) # Get all active offers primarily, but we need all really?
        # db.get_offers returns only active ones if recruteur_id is None in current implementation?
        # Let's check db.get_offers implementation in database.py
        # It says: if recruteur_id: ... else: SELECT * FROM offres WHERE statut = 'actif'
        
        # We need to analyze offers even if they are 'clôturé' if they missed analysis?
        # Or specifically check for 'actif' ones that just expired.
        # Actually we should probably check ALL offers or have a specific query. 
        # But for now, let's stick to 'actif' offers that might have expired just now,
        # OR offers that are closed but might have pending CVs (though usually closing implies done).
        
        # For simplicity/safety, let's fetch ALL offers using a direct query or modify get_offers.
        # But since I can't easily modify get_offers signature without breaking things, let's use a raw query here 
        # or use get_offers(None) if it covers enough.
        # Actually, let's iterate 'actif' offers. If they are expired, we analyze AND maybe close them?
        
        # Let's define a safe connection here
        conn = db.sqlite3.connect(db.DB_NAME)
        conn.row_factory = db.sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM offres")
        all_jobs = c.fetchall()
        conn.close()
        
        controller = RecruitmentController()
        
        for job in all_jobs:
            # Check if deadline passed
            deadline_str = str(job['date_limite'])
            try:
                # Handle both YYYY-MM-DD and YYYY-MM-DD HH:MM:SS
                if len(deadline_str) > 10:
                     deadline_dt = datetime.datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
                else:
                     deadline_dt = datetime.datetime.strptime(deadline_str, "%Y-%m-%d")
                     # Default to end of day? Or start? usually 00:00
                
                if datetime.datetime.now() > deadline_dt:
                    # Expired!
                    # Check for unanalyzed apps
                    apps = db.get_postulations_for_offer(job['id'])
                    
                    # identify unanalyzed
                    unanalyzed = [app for app in apps if not app['score'] and app['cv_url']]
                    
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
                                 fname = res['filename']
                                 score = res['score']
                                 if fname in app_map:
                                     # Update DB
                                     db.update_postulation_results(app_map[fname], score, res)
                        
                        print("Auto-analysis complete.")
                        
            except ValueError:
                continue # Bad date format

    except Exception as e:
        print(f"Error in auto-analysis: {e}")
