import streamlit as st
import database as db
from app_logic.controller import RecruitmentController
import pandas as pd
import os
import datetime
import importlib
importlib.reload(db)

def render_recruiter_space():
    st.header(f"👔 Espace Recruteur - {st.session_state['username']}")
    st.markdown("---")
    
    menu = st.sidebar.radio("Navigation", ["Ajouter une offre", "Gérer mes offres"])
    
    if menu == "Ajouter une offre":
        st.subheader("➕ Créer une nouvelle offre d'emploi")
        with st.form("job_form"):
            title = st.text_input("Titre du poste")
            desc = st.text_area("Description du poste")
            skills = st.text_area("Compétences requises (séparées par des virgules)")
            exp = st.number_input("Expérience minimum (années)", min_value=0)
            
            col1, col2 = st.columns(2)
            with col1:
                deadline_date = st.date_input("Date limite de candidature")
            with col2:
                deadline_time = st.time_input("Heure limite de candidature")
            
            submit = st.form_submit_button("Publier l'offre")
            
            if submit:
                if title and skills:
                    # Combine date and time
                    deadline = datetime.datetime.combine(deadline_date, deadline_time)
                    
                    db.create_job(title, desc, skills, exp, deadline, st.session_state['user_id'])
                    st.success("Offre publiée avec succès !")
                else:
                    st.error("Le titre et les compétences sont obligatoires.")

    elif menu == "Gérer mes offres":
        st.subheader("📋 Mes Offres publiées")
        jobs = db.get_jobs(recruiter_id=st.session_state['user_id'])
        
        for job in jobs:
            with st.expander(f"{job['title']} - {job['status']}"):
                st.write(f"**Description:** {job['description']}")
                st.write(f"**Compétences:** {job['skills_required']}")
                st.write(f"**Deadline:** {job['deadline']}")
                
                # Show Applications
                apps = db.get_applications_for_job(job['id'])
                st.write(f"📊 **{len(apps)} Candidature(s)**")
                
                if apps:
                    # Convert to minimal DF for display
                    app_data = []
                    for app in apps:
                        app_data.append({
                            "Candidat": app['candidate_name'],
                            "Date": app['upload_date'],
                            "Score": app['score'] if app['score'] is not None else "Non analysé",
                            "Compétences": app['skills'] if 'skills' in app.keys() and app['skills'] else "N/A",
                            "CV": app['cv_filepath']
                        })
                    st.dataframe(pd.DataFrame(app_data))

                    # VISUALIZATIONS
                    if apps:
                        scores = [a['Score'] for a in app_data if a['Score'] != "Non analysé"]
                        if scores:
                            st.write("### 📈 Statistiques des Candidatures")
                            col_stat1, col_stat2 = st.columns(2)
                            with col_stat1:
                                st.metric("Score Moyen", f"{sum(scores)/len(scores):.2f}/100")
                            with col_stat2:
                                st.metric("Meilleur Score", f"{max(scores)}/100")
                            
                            # Bar Chart of Scores
                            chart_data = pd.DataFrame(app_data)
                            # Clean data for chart
                            chart_data = chart_data[chart_data['Score'] != "Non analysé"]
                            if not chart_data.empty:
                                chart_data['Score'] = chart_data['Score'].astype(float)
                                st.bar_chart(chart_data, x="Candidat", y="Score")

                            # EXPORT BUTTON
                            csv = pd.DataFrame(app_data).to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Télécharger le rapport (CSV)",
                                data=csv,
                                file_name=f"rapport_{job['title']}.csv",
                                mime="text/csv",
                                key=f"dl_{job['id']}"
                            )
                    
                    # ANALYZE BUTTON
                    if st.button(f"🚀 Analyser les CVs pour '{job['title']}'", key=f"analyze_{job['id']}"):
                        with st.spinner("Analyse en cours..."):
                            controller = RecruitmentController()
                            required_skills = [s.strip() for s in job['skills_required'].split(',') if s.strip()]
                            
                            class FileWrapper:
                                def __init__(self, path):
                                    self.name = os.path.basename(path)
                                    self.path = path
                                def getbuffer(self):
                                    with open(self.path, "rb") as f:
                                        return f.read()

                            # Gather files that need analysis
                            files_to_process = []
                            app_map = {} # Map filename to app_id
                            
                            for app in apps:
                                f_path = app['cv_filepath']
                                if os.path.exists(f_path):
                                    wrapper = FileWrapper(f_path)
                                    files_to_process.append(wrapper)
                                    app_map[wrapper.name] = app['id']
                            
                            if files_to_process:
                                results = controller.process_uploads(files_to_process, required_skills)
                                
                                # Update DB with scores AND skills
                                for res in results:
                                    fname = res['filename']
                                    score = res['score']
                                    skills = res['skills']
                                    if fname in app_map:
                                        db.update_application_results(app_map[fname], score, skills)
                                
                                st.success("Analyse terminée ! Scores et Compétences mis à jour.")
                                st.rerun()
                            else:
                                st.warning("Aucun fichier CV trouvé sur le disque.")
