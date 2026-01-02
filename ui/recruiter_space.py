import streamlit as st
import database as db
from app_logic.controller import RecruitmentController
import pandas as pd
import os
import datetime
import importlib
import json
importlib.reload(db)

from streamlit_option_menu import option_menu


@st.dialog("Ajouter une offre")
def add_offer_dialog():
    st.write("Remplissez les informations ci-dessous pour créer une nouvelle offre.")
    with st.form("new_job_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Titre du poste", key="new_job_title")
        with col2:
            domaine = st.text_input("Domaine (ex: IT, Finance...)", key="new_job_domain")
        
        desc = st.text_area("Description du poste", key="new_job_desc")
        skills = st.text_area("Compétences requises (séparées par des virgules)", key="new_job_skills_unique_v2")
        # Ensure unique keys for all inputs

        c1, c2 = st.columns(2)
        with c1:
            exp = st.number_input("Expérience minimum (années)", min_value=0, key="new_job_exp")
        with c2:
            nb_postes = st.number_input("Nombre de postes à pourvoir", min_value=1, value=1, key="new_job_nb")
        
        col3, col4 = st.columns(2)
        with col3:
            deadline_date = st.date_input("Date limite de candidature")
        with col4:
            # Default to current time for standard workday deadlines or immediate
            default_time = datetime.datetime.now().time()
            deadline_time = st.time_input("Heure limite de candidature", value=default_time)
        
        submit = st.form_submit_button("Publier l'offre")
        
        if submit:
            if title and skills and domaine:
                # Combine date and time
                deadline_dt = datetime.datetime.combine(deadline_date, deadline_time)
                deadline = deadline_dt.strftime("%Y-%m-%d %H:%M:%S")
                
                db.create_offer(title, desc, skills, exp, deadline, st.session_state['user_id'], domaine, nb_postes)
                st.success("Offre publiée avec succès !")
                st.rerun()
            else:
                st.error("Le titre, le domaine et les compétences sont obligatoires.")

def render_recruiter_space():
    st.header(f"👔 Espace Recruteur")
    st.markdown("---")
    
    with st.sidebar:
        menu = option_menu(
            menu_title=None,
            options=["Mes Offres", "Mon Profil", "Statistiques"],
            icons=["briefcase-fill", "person-badge-fill", "bar-chart-fill"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#6C5CE7", "font-size": "1.1rem"}, 
                "nav-link": {"font-size": "15px", "margin":"8px", "border-radius": "8px"},
                "nav-link-selected": {"background-color": "#6C5CE7", "font-weight": "600"},
            }
        )
    
    if menu == "Mes Offres":
        col_header, col_btn = st.columns([0.8, 0.2])
        with col_header:
            st.subheader("📋 Gestion de mes Offres")
        with col_btn:
            if st.button("➕ Ajouter une offre", type="primary", use_container_width=True):
                add_offer_dialog()
        st.markdown("---")
        jobs = db.get_offers(recruteur_id=st.session_state['user_id'])
        
        if not jobs:
            st.info("Vous n'avez publié aucune offre.")
            
        for job in jobs:
            with st.expander(f"{job['titre']} ({job['domaine']}) - {job['statut']}"):
                # State management for editing
                is_editing = st.session_state.get(f"edit_{job['id']}", False)

                if is_editing:
                    st.info("Mode Édition")
                    with st.form(key=f"edit_form_{job['id']}"):
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            u_titre = st.text_input("Titre", value=job['titre'])
                            u_domaine = st.text_input("Domaine", value=job['domaine'])
                        with col_e2:
                            # Handle date parsing
                            try:
                                d_str = str(job['date_limite'])
                                if len(d_str) > 10:
                                    dt_val = datetime.datetime.strptime(d_str, "%Y-%m-%d %H:%M:%S")
                                    d_val = dt_val.date()
                                    t_val = dt_val.time()
                                else:
                                    d_val = datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
                                    t_val = datetime.time(0, 0)
                            except:
                                d_val = datetime.date.today()
                                t_val = datetime.time(0, 0)
                            
                            u_date = st.date_input("Date limite", value=d_val)
                            u_time = st.time_input("Heure limite", value=t_val)
                            
                            u_status = st.selectbox("Statut", ["actif", "clôturé"], index=0 if job['statut'] == 'actif' else 1)
                        
                        u_desc = st.text_area("Description", value=job['description'])
                        u_skills = st.text_area("Compétences", value=job['competences_requises'])
                        c_edit1, c_edit2 = st.columns(2)
                        with c_edit1:
                            u_exp = st.number_input("Expérience Min (années)", value=job['experience_min'] or 0, min_value=0)
                        with c_edit2:
                            current_nb = job['nombre_postes'] if 'nombre_postes' in job.keys() else 1
                            if current_nb is None: current_nb = 1 # Handle potential NULLs
                            u_nb_postes = st.number_input("Nombre de postes", value=current_nb, min_value=1)
                        
                        if st.form_submit_button("💾 Enregistrer les modifications"):
                            # Combine date and time
                            u_deadline_dt = datetime.datetime.combine(u_date, u_time)
                            u_deadline_str = u_deadline_dt.strftime("%Y-%m-%d %H:%M:%S")
                            
                            db.update_offer(job['id'], u_titre, u_desc, u_skills, u_exp, u_deadline_str, u_domaine, u_status, u_nb_postes)
                            st.session_state[f"edit_{job['id']}"] = False
                            st.success("Offre mise à jour avec succès !")
                            st.rerun()
                    
                    if st.button("Annuler", key=f"cancel_{job['id']}"):
                        st.session_state[f"edit_{job['id']}"] = False
                        st.rerun()

                else:
                    # Display Mode
                    c1, c2 = st.columns([0.85, 0.15])
                    with c1:
                        st.write(f"**Description:** {job['description']}")
                        st.write(f"**Compétences:** {job['competences_requises']}")
                        st.write(f"**Deadline:** {job['date_limite']}")
                    with c2:
                        if st.button("✏️", key=f"btn_edit_{job['id']}", help="Modifier l'offre"):
                            st.session_state[f"edit_{job['id']}"] = True
                            st.rerun()
                
                # Show Applications
                apps = db.get_postulations_for_offer(job['id'])
                st.write(f"📊 **{len(apps)} Candidature(s)**")
                
                if apps:
                    # Convert to minimal DF for display
                    app_data = []
                    for app in apps:
                        # Parse JSON results if available
                        skills_detected = "N/A"
                        if app['donnees_analysees']:
                            try:
                                data = json.loads(app['donnees_analysees'])
                                skills_detected = ", ".join(data.get('skills', []))
                            except:
                                skills_detected = "Erreur parsing"

                        app_data.append({
                            "Candidat": f"{app['prenom']} {app['nom']}",
                            "Email": app['email'],
                            "Date": app['date_postulation'],
                            "Score": app['score'] if app['score'] is not None else "Non analysé",
                            "Compétences Détectées": skills_detected,
                            "CV": app['cv_url']
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
                            chart_data = chart_data[chart_data['Score'] != "Non analysé"]
                            if not chart_data.empty:
                                chart_data['Score'] = chart_data['Score'].astype(float)
                                st.bar_chart(chart_data, x="Candidat", y="Score")

                            # EXPORT BUTTON
                            csv = pd.DataFrame(app_data).to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Télécharger le rapport (CSV)",
                                data=csv,
                                file_name=f"rapport_{job['titre']}.csv",
                                mime="text/csv",
                                key=f"dl_{job['id']}"
                            )
                    
                    # ANALYZE BUTTON
                    if st.button(f"🚀 Analyser les CVs pour '{job['titre']}'", key=f"analyze_{job['id']}"):
                        with st.spinner("Analyse en cours..."):
                            controller = RecruitmentController()
                            required_skills = [s.strip() for s in job['competences_requises'].split(',') if s.strip()]
                            
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
                                f_path = app['cv_url']
                                if f_path and os.path.exists(f_path):
                                    wrapper = FileWrapper(f_path)
                                    files_to_process.append(wrapper)
                                    app_map[wrapper.name] = app['id']
                            
                            if files_to_process:
                                results = controller.process_uploads(files_to_process, required_skills)
                                
                                # Update DB with scores AND full JSON results
                                for res in results:
                                    fname = res['filename']
                                    score = res['score']
                                    # res contains 'skills', 'score', 'filename' etc.
                                    # We store the whole res dict (minus maybe binary data if any) as JSON
                                    if fname in app_map:
                                        db.update_postulation_results(app_map[fname], score, res)
                                
                                st.success("Analyse terminée ! Scores et Compétences mis à jour.")
                                st.rerun()
                            else:
                                 st.warning("Aucun fichier CV trouvé sur le disque.")

    elif menu == "Mon Profil":
        st.title("👤 Profil Recruteur")
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        with col1:
             st.markdown(f"""
                <div style="text-align: center; padding: 20px; background: white; border-radius: 15px; border: 1px solid #E0E0E0;">
                    <div style="width: 100px; height: 100px; background: #6C5CE7; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 3rem; margin: 0 auto 15px;">
                        {st.session_state['username'][0].upper()}
                    </div>
                    <h3 style="margin: 0;">{st.session_state['username']}</h3>
                    <p style="color: #636E72;">{st.session_state['role']}</p>
                </div>
             """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("Informations Professionnelles")
            with st.form("profile_form_rec"):
                st.text_input("Nom Complet", value=st.session_state['username'], disabled=True)
                st.text_input("Entreprise / Domaine", value="RecrutIQ Tech")
                st.text_input("Poste", value="Responsable RH")
                
                if st.form_submit_button("Enregistrer les modifications"):
                    st.success("Profil mis à jour avec succès !")

    elif menu == "Statistiques":
        st.subheader("📊 Tableau de Bord des Offres")
        st.markdown("---")
        
        jobs = db.get_offers(recruteur_id=st.session_state['user_id'])
        
        if not jobs:
            st.info("Aucune offre disponible pour afficher les statistiques.")
        else:
            job_titles = {job['titre']: job for job in jobs}
            selected_job_title = st.selectbox("Sélectionnez une offre :", list(job_titles.keys()))
            
            if selected_job_title:
                selected_job = job_titles[selected_job_title]
                apps = db.get_postulations_for_offer(selected_job['id'])
                
                if not apps:
                    st.warning("Aucune candidature trouvée pour cette offre.")
                else:
                    # Calculate Stats
                    total_candidates = len(apps)
                    scores = [app['score'] for app in apps if app['score'] is not None]
                    avg_score = sum(scores) / len(scores) if scores else 0
                    max_score = max(scores) if scores else 0
                    
                    # Display KPIs
                    kpi1, kpi2, kpi3 = st.columns(3)
                    kpi1.metric("Total Candidats", total_candidates)
                    kpi2.metric("Score Moyen", f"{avg_score:.2f}/100")
                    kpi3.metric("Meilleur Score", f"{max_score}/100")
                    
                    st.markdown("---")
                    
                    # Graph 1: Score Distribution (Bar Chart)
                    st.write("### Distribution des Scores")
                    chart_data = []
                    all_skills = []
                    
                    for app in apps:
                        # Prepare score data
                        if app['score'] is not None:
                            chart_data.append({
                                "Candidat": f"{app['prenom']} {app['nom']}",
                                "Score": app['score']
                            })
                        
                        # Collect skills
                        if app['donnees_analysees']:
                            try:
                                data = json.loads(app['donnees_analysees'])
                                if 'skills' in data:
                                    all_skills.extend(data['skills'])
                            except:
                                pass

                    if chart_data:
                        df_scores = pd.DataFrame(chart_data)
                        st.bar_chart(df_scores, x="Candidat", y="Score")
                    else:
                        st.info("Aucune donnée de score disponible.")

                    # Graph 2: Top Skills (Horizontal Bar Chart ?)
                    st.write("### Compétences les plus fréquentes")
                    if all_skills:
                        from collections import Counter
                        skills_counts = Counter(all_skills)
                        df_skills = pd.DataFrame.from_dict(skills_counts, orient='index', columns=['Count']).sort_values(by='Count', ascending=False).head(10)
                        st.bar_chart(df_skills)
                    else:
                        st.info("Aucune compétence détectée.")

                    # Candidate Selection (Top N) - Only if status is Closed OR Deadline passed
                    is_closed = selected_job['statut'] == 'clôturé'
                    # Check date/time
                    try:
                        d_str = str(selected_job['date_limite'])
                        if len(d_str) > 10:
                            deadline_dt = datetime.datetime.strptime(d_str, "%Y-%m-%d %H:%M:%S")
                            is_past_deadline = datetime.datetime.now() > deadline_dt
                        else:
                            # Fallback for old dates (YYYY-MM-DD) - assume end of day or strict date > today
                            deadline_d = datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
                            is_past_deadline = datetime.date.today() > deadline_d
                    except Exception as e:
                        is_past_deadline = False
                    
                    if is_closed or is_past_deadline:
                        st.markdown("---")
                        st.write("### 🏆 Candidats Sélectionnés")
                        if not is_closed:
                             st.info(f"La date limite ({selected_job['date_limite']}) est passée, voici les candidats retenus provisoirement basés sur le score.")
                        
                        nb_postes = selected_job['nombre_postes'] if 'nombre_postes' in selected_job.keys() else 1
                        if nb_postes is None: nb_postes = 1

                        # Sort apps by score descending
                        # Filter out None scores
                        scored_apps = [a for a in apps if a['score'] is not None and a['score'] > 0]
                        scored_apps.sort(key=lambda x: x['score'], reverse=True)
                        
                        selected = scored_apps[:nb_postes]
                        rejected = scored_apps[nb_postes:] # Or just the rest
                        
                        if selected:
                            st.success(f"Top {len(selected)} candidat(s) pour {nb_postes} poste(s).")
                            sel_data = []
                            for s in selected:
                                sel_data.append({
                                    "Nom": f"{s['prenom']} {s['nom']}",
                                    "Score": s['score'],
                                    "Email": s['email'],
                                    "Statut": "ACCEPTED ✅"
                                })
                            st.table(pd.DataFrame(sel_data))
                        else:
                            st.warning("Aucun candidat n'a de score suffisant pour être sélectionné.")

                        if rejected:
                            with st.expander("Voir les candidats non retenus"):
                                rej_data = []
                                for r in rejected:
                                    rej_data.append({
                                        "Nom": f"{r['prenom']} {r['nom']}",
                                        "Score": r['score'], 
                                        "Statut": "REFUSED ❌"
                                    })
                                st.table(pd.DataFrame(rej_data))
                    else:
                        st.info("La sélection des candidats sera disponible une fois l'offre clôturée ou la date limite passée.")
