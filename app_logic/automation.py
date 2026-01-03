from app_logic.email_service import EmailService

def run_pending_analyses():
    """
    Checks for offers where the deadline has passed.
    1. Triggers analysis automatically for unanalyzed apps.
    2. Performs candidate selection (Accepted/Refused) and sends emails.
    """
    try:
        # Get all offers - Fetch raw to be safe
        conn = db.sqlite3.connect(db.DB_NAME)
        conn.row_factory = db.sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM offres")
        all_jobs = c.fetchall()
        
        controller = RecruitmentController()
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
                     # For old date format, assume passed if today > date
                     is_past = datetime.date.today() > deadline_dt.date()
                
                if is_past:
                    # 1. ANALYSIS PHASE
                    apps = db.get_postulations_for_offer(job['id'])
                    unanalyzed = [app for app in apps if not app['score'] and app['cv_url']]
                    
                    if unanalyzed:
                        # ... (Existing Analysis Logic) ...
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
                    
                    # 2. SELECTION & EMAIL PHASE
                    # Refresh apps to get new scores
                    apps = db.get_postulations_for_offer(job['id'])
                    scored_apps = [a for a in apps if a['score'] is not None and a['score'] > 0]
                    scored_apps.sort(key=lambda x: x['score'], reverse=True)
                    
                    nb_postes = job['nombre_postes'] if job['nombre_postes'] else 1
                    
                    selected = scored_apps[:nb_postes]
                    refused = scored_apps[nb_postes:]
                    
                    # Process Selected
                    for cand in selected:
                        # Check if already notified
                        # Fetch 'email_envoye' from row. 
                        # Note: 'apps' comes from get_postulations_for_offer which selects p.*
                        # If column was just added, it might be 0/None.
                        
                        is_sent = cand['email_envoye']
                        current_status = cand['statut']
                        
                        if not is_sent:
                            print(f"Selecting candidate {cand['nom']} for job {job['titre']}")
                            # Send Email
                            sent = email_service.send_acceptance_email(cand['email'], f"{cand['prenom']} {cand['nom']}", job['titre'])
                            if sent:
                                db.update_postulation_status(cand['id'], "Accepted", email_envoye=True)
                        elif current_status != "Accepted":
                             # Ensure status is correct even if email sent (or manual update)
                             db.update_postulation_status(cand['id'], "Accepted", email_envoye=True)

                    # Process Refused
                    for cand in refused:
                        if cand['statut'] != "Refused":
                            db.update_postulation_status(cand['id'], "Refused", email_envoye=False)
                            
            except ValueError:
                continue 

        conn.close()

    except Exception as e:
        print(f"Error in auto-analysis/selection: {e}")

