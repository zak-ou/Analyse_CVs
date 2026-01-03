import streamlit as st
import database as db
from app_logic.controller import RecruitmentController
import pandas as pd
import plotly.express as px
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
            options=["Mes Offres", "Statistiques", "Mon Profil"],
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



                    # EXPORT BUTTON

                    
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
        # --- Modern Profile Design ---
        st.markdown("""
        <style>
            .profile-header {
                background: linear-gradient(135deg, #6C5CE7 0%, #a29bfe 100%);
                padding: 40px;
                border-radius: 20px;
                display: flex;
                align-items: center;
                color: white;
                margin-bottom: 30px;
                box-shadow: 0 10px 20px rgba(108, 92, 231, 0.2);
            }
            .profile-avatar {
                width: 100px;
                height: 100px;
                background-color: white;
                color: #6C5CE7;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 40px;
                font-weight: bold;
                margin-right: 25px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            }
            .profile-info h1 {
                margin: 0;
                font-size: 2.2rem;
                font-weight: 700;
                color: white !important;
            }
            .profile-info p {
                margin: 5px 0 0 0;
                font-size: 1.1rem;
                opacity: 0.9;
            }
            .info-card {
                background: white;
                padding: 25px;
                border-radius: 15px;
                border: 1px solid #f0f2f6;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
        </style>
        """, unsafe_allow_html=True)

        # Header Section
        st.markdown(f"""
        <div class="profile-header">
            <div class="profile-avatar">{st.session_state['username'][0].upper()}</div>
            <div class="profile-info">
                <h1>{st.session_state['username']}</h1>
                <p>{st.session_state['role']} chez RecrutIQ</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Main Content Grid
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.markdown("### 📌 Détails du Compte")
            with st.container(): # mimicking card via css above if applied globally, or just cleaner layout
                 st.info(f"**Email:** {db.verify_user(st.session_state['username'], 'dummy', 'Recruteur')['email'] if False else 'utilisateur@example.com'}") # Placeholder logic fix later or just display known
                 st.write(f"**Rôle:** {st.session_state['role']}")
                 st.write("**Statut:** Actif ✅")
        
        with c2:
            st.markdown("### ✏️ Mise à jour des Informations")
            with st.form("profile_form_rec_modern"):
                c_form1, c_form2 = st.columns(2)
                with c_form1:
                    st.text_input("Nom Complet", value=st.session_state['username'])
                    st.text_input("Téléphone", value="+212 600 000 000")
                with c_form2:
                    st.text_input("Entreprise", value="RecrutIQ Tech")
                    st.text_input("Site Web", value="www.recrutiq.com")
                
                st.text_area("Bio / Description", value="Responsable des ressources humaines passionné par la tech.")
                
                if st.form_submit_button("Sauvegarder les modifications", type="primary"):
                    st.success("Profil mis à jour avec succès !")

    elif menu == "Statistiques":
        st.subheader("📊 Tableau de Bord des Offres")
        st.markdown("---")
        
        jobs = db.get_offers(recruteur_id=st.session_state['user_id'])
        
        if not jobs:
            st.info("Aucune offre disponible pour afficher les statistiques.")
        else:
            # Dropdown for selecting a job
            job_titles = {job['titre']: job for job in jobs}
            selected_job_title = st.selectbox("Sélectionnez une offre :", list(job_titles.keys()))
            
            if selected_job_title:
                selected_job = job_titles[selected_job_title]
                apps = db.get_postulations_for_offer(selected_job['id'])
                
                if not apps:
                    st.warning("Aucune candidature trouvée pour cette offre.")
                else:
                    # --- Data Preparation ---
                    app_data = []
                    all_skills = []
                    
                    for app in apps:
                        score = app['score'] if app['score'] is not None else 0
                        # Parse skills
                        skills = []
                        if app['donnees_analysees']:
                            try:
                                data = json.loads(app['donnees_analysees'])
                                if 'skills' in data:
                                    skills = data['skills']
                                    all_skills.extend(skills)
                            except:
                                pass
                        
                        app_data.append({
                            "Candidat": f"{app['prenom']} {app['nom']}",
                            "Email": app['email'],
                            "Date": app['date_postulation'],
                            "Score": score,
                            "Compétences": ", ".join(skills),
                            "CV": app['cv_url']
                        })
                    
                    df_apps = pd.DataFrame(app_data)
                    df_apps['Date'] = pd.to_datetime(df_apps['Date'])

                    # --- 1. KPIs ---
                    total_candidates = len(apps)
                    scored_apps = [a for a in app_data if a['Score'] > 0]
                    avg_score = sum(x['Score'] for x in scored_apps) / len(scored_apps) if scored_apps else 0
                    max_score = max(x['Score'] for x in scored_apps) if scored_apps else 0
                    
                    k1, k2, k3 = st.columns(3)
                    k1.metric("Total Candidats", total_candidates)
                    k2.metric("Score Moyen", f"{avg_score:.2f}/100")
                    k3.metric("Meilleur Score", f"{max_score}/100")
                    
                    st.markdown("---")

                    # --- 2. Visualizations ---
                    st.write("### 📈 Analyse Visuelle")
                    
                    tab1, tab2, tab3 = st.columns(3)
                    
                    with tab1:
                        st.caption("Distribution des Scores")
                        if not df_apps.empty and scored_apps:
                             fig_hist = px.histogram(df_apps[df_apps['Score'] > 0], x="Score", nbins=20, 
                                                    title="Répartition des Scores", color_discrete_sequence=['#6C5CE7'])
                             fig_hist.update_layout(bargap=0.2, showlegend=False, height=300)
                             st.plotly_chart(fig_hist, use_container_width=True)
                        else:
                            st.info("Scores non disponibles.")
                            
                    with tab2:
                        st.caption("Chronologie des Candidatures")
                        if not df_apps.empty:
                            apps_per_day = df_apps.groupby(df_apps['Date'].dt.date).size().reset_index(name='Comptes')
                            fig_line = px.line(apps_per_day, x='Date', y='Comptes', markers=True, 
                                              title="Candidatures par Date", color_discrete_sequence=['#00b894'])
                            fig_line.update_layout(height=300)
                            st.plotly_chart(fig_line, use_container_width=True)
                    
                    with tab3:
                         st.caption("Top Compétences")
                         if all_skills:
                             from collections import Counter
                             skills_counts = Counter(all_skills).most_common(10)
                             df_skills = pd.DataFrame(skills_counts, columns=['Skill', 'Count'])
                             fig_bar = px.bar(df_skills, x='Count', y='Skill', orientation='h', 
                                             title="Top 10 Compétences", color='Count', color_continuous_scale='Bluered')
                             fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=300)
                             st.plotly_chart(fig_bar, use_container_width=True)
                         else:
                             st.info("Pas de compétences détectées.")

                    st.markdown("---")

                    # --- 3. Detailed List ---
                    st.write("### 📋 Liste Détaillée des Candidats")
                    
                    # Configure columns for st.dataframe
                    st.dataframe(
                        df_apps[['Candidat', 'Email', 'Date', 'Score', 'Compétences', 'CV']],
                        use_container_width=True,
                        column_config={
                            "Date": st.column_config.DateColumn(
                                "Date Postulation",
                                format="DD/MM/YYYY"
                            ),
                            "Score": st.column_config.ProgressColumn(
                                "Score",
                                format="%.1f / 100",
                                min_value=0,
                                max_value=100,
                            ),
                            "CV": st.column_config.LinkColumn(
                                "Lien CV",
                                display_text="Voir CV"
                            ),
                            "Email": st.column_config.TextColumn("Email")
                        },
                        hide_index=True
                    )

                    st.markdown("---")
                    # EXPORT BUTTON
                    csv_stat = pd.DataFrame(app_data).to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Télécharger le rapport (CSV)",
                        data=csv_stat,
                        file_name=f"rapport_{selected_job['titre']}.csv",
                        mime="text/csv",
                        key=f"dl_stat_{selected_job['id']}"
                    )

