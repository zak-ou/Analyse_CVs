import streamlit as st
import database as db
import os
import json
import datetime
from streamlit_option_menu import option_menu

def render_candidate_space():
    # --- 1. CSS AVANCÉ POUR DESIGN TYPE "CARTE" ---
    st.markdown("""
    <style>
        /* Personnalisation des conteneurs Streamlit pour ressembler à des cartes */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px;
            border: 1px solid #F0F0F0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            padding: 15px;
            transition: all 0.3s ease;
        }
        
        /* Effet au survol de la carte (La carte monte légèrement) */
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #6C5CE7;
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(108, 92, 231, 0.1);
        }

        /* Style des Titres de jobs */
        .job-title {
            color: #2D3436;
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 5px;
            font-family: 'Segoe UI', sans-serif;
        }

        /* Style des métadonnées (Date, Expérience) */
        .job-meta {
            color: #636E72;
            font-size: 13px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }

        /* Description tronquée */
        .job-desc {
            font-size: 14px;
            color: #555;
            line-height: 1.5;
            margin-bottom: 15px;
            height: 60px; /* Force une hauteur pour aligner les boutons */
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
        }

        /* Tags de compétences */
        .skill-pill {
            display: inline-block;
            background-color: #F3F0FF; /* Fond violet très clair */
            color: #6C5CE7;           /* Texte Indigo */
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 11px;
            font-weight: 600;
            margin-right: 5px;
            margin-bottom: 5px;
        }

        /* Bouton "Voir l'offre" personnalisé */
        .stButton button {
            background-color: #6C5CE7;
            color: white;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            transition: background 0.3s;
        }
        .stButton button:hover {
            background-color: #5641cc;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. SIDEBAR (NAVIGATION) ---
    with st.sidebar:
        # Menus are now handled here, profile is handled in app.py
        
        menu = option_menu(
            menu_title=None,
            options=["Offres d'Emploi", "Mes Candidatures", "Mon Profil", "Générer mon CV"],
            icons=["briefcase-fill", "file-earmark-check-fill", "person-fill", "file-earmark-pdf-fill"], 
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#6C5CE7", "font-size": "1.1rem"}, 
                "nav-link": {"font-size": "15px", "margin":"8px", "border-radius": "8px"},
                "nav-link-selected": {"background-color": "#6C5CE7", "font-weight": "600"},
            }
        )

    # --- 3. FONCTION POPUP (DIALOG) ---
    @st.dialog("Détails de l'opportunité")
    def show_job_dialog(job):
        # En-tête du popup
        st.markdown(f"""
        <h2 style='color:#6C5CE7; margin-bottom:5px;'>{job['titre']}</h2>
        <h4 style='color:#888; margin-top:0;'>Domaine: {job['domaine']}</h4>
        <div style='display:flex; gap:15px; color:#666; font-size:14px; margin-bottom:20px;'>
            <span>📅 Date limite : <b>{job['date_limite']}</b></span>
            <span>🎓 Expérience min : <b>{job['experience_min']} ans</b></span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📝 Description du poste")
        st.info(job['description'])

        st.markdown("#### 🛠 Compétences requises")
        skills_html = "".join([f"<span class='skill-pill'>{s.strip()}</span>" for s in job['competences_requises'].split(',')])
        st.markdown(skills_html, unsafe_allow_html=True)
        
        st.divider()
        # Check if already applied to change button label
        has_applied = False
        apps = db.get_postulations_for_candidate(st.session_state['user_id'])
        for a in apps:
            if a['offre_id'] == job['id']:
                has_applied = True
                break
        
        st.markdown("#### 🚀 " + ("Mettre à jour ma candidature" if has_applied else "Postuler"))
        if has_applied:
            st.info("💡 Vous avez déjà postulé à cette offre. En envoyant un nouveau CV, votre score sera réinitialisé et votre candidature sera réévaluée.")
            
        uploaded_cv = st.file_uploader("Déposez votre CV (PDF uniquement)", type=['pdf'], key=f"cv_up_{job['id']}")
        
        btn_label = "Mettre à jour mon CV" if has_applied else "Envoyer ma candidature"
        if st.button(btn_label, type="primary", width="stretch", key=f"btn_submit_{job['id']}"):
            if uploaded_cv:
                # Sauvegarde locale
                upload_dir = "data/uploads"
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, f"{st.session_state['user_id']}_{uploaded_cv.name}")
                with open(file_path, "wb") as f:
                    f.write(uploaded_cv.getbuffer())
                
                # Sauvegarde BDD
                success = False
                if has_applied:
                    success = db.update_postulation(job['id'], st.session_state['user_id'], file_path)
                    msg = "Votre candidature a été mise à jour avec succès !"
                else:
                    success = db.submit_postulation(job['id'], st.session_state['user_id'], file_path)
                    msg = "Votre CV a été transmis au recruteur ! Un email de confirmation vous a été envoyé."

                if success:
                    # Envoi d'email de confirmation (même pour mise à jour)
                    try:
                        from app_logic.email_service import EmailService
                        email_service = EmailService()
                        email_service.send_confirmation_email(
                            st.session_state.get('user_email'),
                            st.session_state['username'],
                            job['titre']
                        )
                    except:
                        pass

                    st.balloons()
                    st.success(msg)
                    import time
                    time.sleep(2)
                    st.rerun()
            else:
                st.error("N'oubliez pas d'ajouter votre CV !")

    # --- 4. CONTENU PRINCIPAL ---
    
    # 📌 ONGLET : OFFRES D'EMPLOI
    if menu == "Offres d'Emploi":
        st.markdown("<h2 style='color:#262730;'>💼 Dernières opportunités</h2>", unsafe_allow_html=True)
        st.caption("Consultez les offres et postulez directement.")
        
        # --- FILTRES ET RECHERCHE ---
        with st.container(border=True):
            col_search, col_f1, col_f2 = st.columns([2, 1, 1])
            with col_search:
                search_query = st.text_input("🔍 Rechercher un poste", placeholder="Ex: Développeur Python...")
            
            jobs_all = db.get_offers()
            domains = sorted(list(set([j['domaine'] for j in jobs_all if j['domaine']])))
            
            with col_f1:
                filter_domain = st.selectbox("Domaine", ["Tous"] + domains)
            with col_f2:
                filter_exp = st.number_input("Expérience Max (ans)", min_value=0, max_value=20, value=20)

        st.markdown("---")

        # Filtrage de la liste
        jobs = []
        for j in jobs_all:
            # Filtre Recherche
            if search_query and search_query.lower() not in j['titre'].lower() and search_query.lower() not in j['description'].lower():
                continue
            # Filtre Domaine
            if filter_domain != "Tous" and j['domaine'] != filter_domain:
                continue
            # Filtre Expérience
            if j['experience_min'] and j['experience_min'] > filter_exp:
                continue
            jobs.append(j)

        if not jobs:
            st.info("🔎 Aucune offre ne correspond à vos critères.")
        else:
            # Création d'une grille propre (2 colonnes)
            cols = st.columns(2) 
            
            for i, job in enumerate(jobs):
                with cols[i % 2]:
                    # LE CŒUR DU DESIGN : Le conteneur sert de carte
                    with st.container(border=True):
                        # 1. Titre
                        st.markdown(f"<div class='job-title'>{job['titre']}</div>", unsafe_allow_html=True)
                        st.caption(f"Domaine : {job['domaine']}")
                        
                        # 2. Métadonnées (Icônes et texte gris)
                        st.markdown(f"""
                        <div class='job-meta'>
                            <span>🗓 {job['date_limite']}</span>
                            <span>⏳ {job['experience_min']} ans d'exp.</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 3. Description (coupée proprement par CSS)
                        st.markdown(f"<div class='job-desc'>{job['description']}</div>", unsafe_allow_html=True)
                        
                        # 4. Tags de compétences (limités à 3 pour ne pas casser le design)
                        skills = job['competences_requises'].split(',')[:3]
                        skills_html = "".join([f"<span class='skill-pill'>{s.strip()}</span>" for s in skills])
                        st.markdown(f"<div style='margin-bottom:15px;'>{skills_html}</div>", unsafe_allow_html=True)
                        
                        # 5. BOUTON INTÉGRÉ
                        if st.button("Voir l'offre & Postuler", key=f"job_{job['id']}", width="stretch"):
                            show_job_dialog(job)

    # --- SECTION : MES CANDIDATURES ---
    elif menu == "Mes Candidatures":
        st.title("Suivi des candidatures")
        
        my_apps = db.get_postulations_for_candidate(st.session_state['user_id'])
        
        if not my_apps:
            st.info("Vous n'avez pas encore postulé.")
        else:
            # Affichage sous forme de liste propre
            for app in my_apps:
                # Check offer state
                offer_status = app['statut_offre'] 
                user_status = app['statut_postulation']
                
                offer_deadline_str = str(app['date_limite'])
                is_closed = offer_status == 'clôturé'
                try:
                    if len(offer_deadline_str) > 10:
                        deadline_dt = datetime.datetime.strptime(offer_deadline_str, "%Y-%m-%d %H:%M:%S")
                        is_past_deadline = datetime.datetime.now() > deadline_dt
                    else:
                        deadline_d = datetime.datetime.strptime(offer_deadline_str, "%Y-%m-%d").date()
                        is_past_deadline = datetime.date.today() > deadline_d
                except:
                    is_past_deadline = False
                
                decision_status = user_status if user_status else "En attente"
                decision_color = "orange"
                
                if decision_status == "Accepted":
                    decision_status = "✅ Sélectionné"
                    decision_color = "green"
                elif decision_status == "Refused":
                    decision_status = "❌ Non retenu"
                    decision_color = "red"
                else:
                    decision_status = "En attente ⏳"
                    decision_color = "orange"
                
                # Display
                is_analyzed = app['donnees_analysees'] is not None
                
                with st.expander(f"{app['titre']} (Postulé le {app['date_postulation']})"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Statut de l'offre:** {'Clôturée' if (is_closed or is_past_deadline) else 'En cours'}")
                        st.markdown(f"**Résultat :** <span style='color:{decision_color}; font-weight:bold;'>{decision_status}</span>", unsafe_allow_html=True)
                        st.write(f"**Fichier :** {os.path.basename(app['cv_url'])}")
                    
                    with col2:
                        score_val = f"{app['score']}/100" if (is_analyzed and app['score']) else "--"
                        st.metric("Votre Score", score_val)
                    
                    if is_analyzed:
                        st.markdown("---")
                        st.caption("Détails de l'analyse automatique :")
                        try:
                            # Try parsing JSON
                            data = json.loads(app['donnees_analysees'])
                            skills_detected = data.get('skills', [])
                            st.write(f"**Compétences détectées :** {', '.join(skills_detected)}")
                        except:
                            st.write("Erreur d'affichage des détails.")

    # --- SECTION : MON PROFIL ---
    elif menu == "Mon Profil":
        import services.profile_service as ps
        
        # Fresh fetch of user data
        user_data = db.get_user_by_id(st.session_state['user_id'], st.session_state['role'])
        if user_data:
            user_data = dict(user_data)
        cv_data = db.get_complete_cv_data(st.session_state['user_id'])
        completion = ps.calculate_candidate_completion(user_data, cv_data)
        
        # 1. PROFILE HEADER
        # Robustly handle image or initials
        avatar_html = user_data['prenom'][0].upper()
        if user_data.get('photo_url') and os.path.exists(user_data['photo_url']):
            try:
                with open(user_data["photo_url"], "rb") as img_file:
                    b64_content = base64.b64encode(img_file.read()).decode()
                    avatar_html = f'<img src="data:image/png;base64,{b64_content}" />'
            except:
                pass

        st.markdown(f"""
<div class="profile-header-container">
<div class="profile-avatar-large">
{avatar_html}
</div>
<div class="profile-name">{user_data['prenom']} {user_data['nom']}</div>
<span class="profile-role-badge">Candidat Actif</span>
<div class="profile-progress-container">
<div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.85rem;">
<span>Complétion du profil</span>
<span>{completion}%</span>
</div>
<div class="profile-progress-bar">
<div class="profile-progress-fill" style="width: {completion}%"></div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

        # 2. PROFILE CONTENT (TABS)
        p_tab1, p_tab2, p_tab3 = st.tabs(["👤 Infos Personnelles", "🌐 Réseaux & Bio", "⚙️ Paramètres"])
        
        with p_tab1:
            with st.form("edit_profile_main"):
                col1, col2 = st.columns(2)
                with col1:
                    u_prenom = st.text_input("Prénom", value=user_data['prenom'])
                    u_nom = st.text_input("Nom", value=user_data['nom'])
                with col2:
                    u_email = st.text_input("Email", value=user_data['email'], disabled=True)
                    u_tele = st.text_input("Numéro de Téléphone", value=user_data['num_tele'] or "")
                
                u_photo = st.file_uploader("Modifier la photo de profil", type=['png', 'jpg', 'jpeg'])
                
                if st.form_submit_button("Sauvegarder les informations", width="stretch", type="primary"):
                    photo_path = user_data['photo_url']
                    if u_photo:
                        os.makedirs("data/profiles", exist_ok=True)
                        photo_path = f"data/profiles/avatar_{st.session_state['user_id']}.png"
                        with open(photo_path, "wb") as f:
                            f.write(u_photo.getbuffer())
                    
                    db.update_candidate_profile(
                        st.session_state['user_id'], 
                        u_tele, 
                        user_data['bio'], 
                        photo_path,
                        user_data['linkedin_url'],
                        user_data['github_url'],
                        user_data['portfolio_url']
                    )
                    st.success("Profil mis à jour avec succès !")
                    st.rerun()

        with p_tab2:
            with st.form("edit_profile_bio"):
                st.markdown("##### Ma Bio")
                u_bio = st.text_area("Décrivez-vous en quelques lignes", value=user_data['bio'] or "", height=150)
                
                st.markdown("##### Mes Réseaux")
                c1, c2 = st.columns(2)
                with c1:
                    u_lin = st.text_input("LinkedIn URL", value=user_data['linkedin_url'] or "", placeholder="https://linkedin.com/in/...")
                    u_git = st.text_input("GitHub URL", value=user_data['github_url'] or "", placeholder="https://github.com/...")
                with c2:
                    u_port = st.text_input("Portfolio URL", value=user_data['portfolio_url'] or "", placeholder="https://mon-site.com")
                
                if st.form_submit_button("Mettre à jour ma bio et mes réseaux", width="stretch", type="primary"):
                    db.update_candidate_profile(
                        st.session_state['user_id'],
                        user_data['num_tele'],
                        u_bio,
                        user_data['photo_url'],
                        u_lin,
                        u_git,
                        u_port
                    )
                    st.success("Informations mises à jour !")
                    st.rerun()

        with p_tab3:
            st.info("Les paramètres de sécurité et de compte seront disponibles prochainement.")
            if st.button("🚪 Déconnexion", width="stretch", type="secondary"):
                st.session_state['logged_in'] = False
                st.rerun()
    
    # --- SECTION : GÉNÉRER MON CV ---
    elif menu == "Générer mon CV":
        st.title("📄 Générer mon CV Professionnel")
        st.caption("Remplissez les informations ci-dessous pour créer votre CV au format PDF")
        st.markdown("---")
        
        # Initialize session state for form data
        if 'cv_education_count' not in st.session_state:
            st.session_state.cv_education_count = 1
        if 'cv_experience_count' not in st.session_state:
            st.session_state.cv_experience_count = 1
        if 'cv_langues_count' not in st.session_state:
            st.session_state.cv_langues_count = 1
        
        # Load existing CV data if available
        existing_data = db.get_complete_cv_data(st.session_state['user_id'])
        coordonnees_data = existing_data['coordonnees']
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📍 Coordonnées", 
            "👤 Profil", 
            "🎓 Éducation", 
            "💼 Expériences", 
            "🛠 Compétences", 
            "🌍 Langues"
        ])
        
        # TAB 1: Coordonnées
        with tab1:
            st.subheader("Coordonnées")
            with st.form("coordonnees_form"):
                nom_complet = st.text_input(
                    "Nom Complet*", 
                    value=coordonnees_data['nom_complet'] if coordonnees_data else "",
                    placeholder="Ex: OUBAIH ZAKARIA"
                )
                email = st.text_input(
                    "Email*", 
                    value=coordonnees_data['email'] if coordonnees_data else "",
                    placeholder="exemple@email.com"
                )
                col1, col2 = st.columns(2)
                with col1:
                    telephone = st.text_input(
                        "Téléphone*", 
                        value=coordonnees_data['telephone'] if coordonnees_data else "",
                        placeholder="+212 675 900 477"
                    )
                with col2:
                    ville_region = st.text_input(
                        "Ville, Région*", 
                        value=coordonnees_data['ville_region'] if coordonnees_data else "",
                        placeholder="Smimou, Essaouira"
                    )
                
                if st.form_submit_button("💾 Enregistrer les coordonnées", width="stretch"):
                    if nom_complet and email and telephone and ville_region:
                        # Save to session state temporarily
                        st.session_state.cv_coordonnees = {
                            'nom_complet': nom_complet,
                            'email': email,
                            'telephone': telephone,
                            'ville_region': ville_region
                        }
                        st.success("✅ Coordonnées enregistrées!")
                    else:
                        st.error("⚠️ Veuillez remplir tous les champs obligatoires (*)")
        
        # TAB 2: Profil
        with tab2:
            st.subheader("Profil Professionnel")
            st.caption("Rédigez un résumé de 3-5 lignes : objectif, formation, motivations, compétences clés")
            with st.form("profil_form"):
                profil = st.text_area(
                    "Résumé*",
                    value=coordonnees_data['profil'] if coordonnees_data else "",
                    height=150,
                    placeholder="Ex: Titulaire d'un Diplôme Universitaire de Technologie en Génie Informatique..."
                )
                
                if st.form_submit_button("💾 Enregistrer le profil", width="stretch"):
                    if profil:
                        if 'cv_coordonnees' not in st.session_state:
                            st.session_state.cv_coordonnees = {}
                        st.session_state.cv_coordonnees['profil'] = profil
                        st.success("✅ Profil enregistré!")
                    else:
                        st.error("⚠️ Veuillez remplir votre profil")
        
        # TAB 3: Éducation
        with tab3:
            st.subheader("Formation Académique")
            
            # Load existing education
            existing_education = existing_data['education']
            if existing_education and st.session_state.cv_education_count == 1:
                st.session_state.cv_education_count = len(existing_education)
            
            education_entries = []
            
            for i in range(st.session_state.cv_education_count):
                with st.expander(f"📚 Formation #{i+1}", expanded=(i==0)):
                    existing_edu = existing_education[i] if i < len(existing_education) else None
                    
                    etablissement = st.text_input(
                        "Établissement", 
                        key=f"edu_etab_{i}",
                        value=existing_edu['etablissement'] if existing_edu else "",
                        placeholder="Ex: École Supérieure de Technologie de Guelmim"
                    )
                    diplome = st.text_input(
                        "Diplôme", 
                        key=f"edu_diplome_{i}",
                        value=existing_edu['diplome'] if existing_edu else "",
                        placeholder="Ex: Diplôme Universitaire de Technologie – DUT"
                    )
                    periode = st.text_input(
                        "Période", 
                        key=f"edu_periode_{i}",
                        value=existing_edu['periode'] if existing_edu else "",
                        placeholder="Ex: 2023–2025"
                    )
                    details = st.text_area(
                        "Détails (un par ligne)", 
                        key=f"edu_details_{i}",
                        value=existing_edu['details'] if existing_edu else "",
                        placeholder="Solides bases en informatique\nProgrammation orientée objet",
                        height=80
                    )
                    
                    if etablissement or diplome:
                        education_entries.append({
                            'etablissement': etablissement,
                            'diplome': diplome,
                            'periode': periode,
                            'details': details
                        })
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("➕ Ajouter une formation", width="stretch"):
                    st.session_state.cv_education_count += 1
                    st.rerun()
            with col2:
                if st.button("💾 Enregistrer l'éducation", width="stretch", type="primary"):
                    st.session_state.cv_education = education_entries
                    st.success("✅ Formations enregistrées!")
        
        # TAB 4: Expériences
        with tab4:
            st.subheader("Expériences Professionnelles")
            
            # Load existing experience
            existing_experience = existing_data['experience']
            if existing_experience and st.session_state.cv_experience_count == 1:
                st.session_state.cv_experience_count = len(existing_experience)
            
            experience_entries = []
            
            for i in range(st.session_state.cv_experience_count):
                with st.expander(f"💼 Expérience #{i+1}", expanded=(i==0)):
                    existing_exp = existing_experience[i] if i < len(existing_experience) else None
                    
                    entreprise = st.text_input(
                        "Entreprise", 
                        key=f"exp_entreprise_{i}",
                        value=existing_exp['entreprise'] if existing_exp else "",
                        placeholder="Ex: Managem – Filiale Akka"
                    )
                    titre_mission = st.text_input(
                        "Titre de la mission", 
                        key=f"exp_titre_{i}",
                        value=existing_exp['titre_mission'] if existing_exp else "",
                        placeholder="Ex: Développement d'une application web"
                    )
                    periode = st.text_input(
                        "Période", 
                        key=f"exp_periode_{i}",
                        value=existing_exp['periode'] if existing_exp else "",
                        placeholder="Ex: Juillet 2023"
                    )
                    realisations = st.text_area(
                        "Réalisations (une par ligne)", 
                        key=f"exp_realisations_{i}",
                        value=existing_exp['realisations'] if existing_exp else "",
                        placeholder="Développement d'une API REST avec Spring Boot\nIntégration d'une base de données MySQL",
                        height=100
                    )
                    
                    if entreprise or titre_mission:
                        experience_entries.append({
                            'entreprise': entreprise,
                            'titre_mission': titre_mission,
                            'periode': periode,
                            'realisations': realisations
                        })
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("➕ Ajouter une expérience", width="stretch"):
                    st.session_state.cv_experience_count += 1
                    st.rerun()
            with col2:
                if st.button("💾 Enregistrer les expériences", width="stretch", type="primary"):
                    st.session_state.cv_experience = experience_entries
                    st.success("✅ Expériences enregistrées!")
        
        # TAB 5: Compétences
        with tab5:
            st.subheader("Compétences")
            
            existing_skills = existing_data['skills']
            
            with st.form("skills_form"):
                st.markdown("**Technical Skills**")
                languages = st.text_input(
                    "Languages", 
                    value=existing_skills['languages'] if existing_skills else "",
                    placeholder="Ex: C, Java, PHP, SQL, JavaScript, Python"
                )
                technologies = st.text_input(
                    "Technologies/Frameworks", 
                    value=existing_skills['technologies'] if existing_skills else "",
                    placeholder="Ex: Spring Boot, Flutter, React JS, Node.js"
                )
                databases = st.text_input(
                    "Database Management", 
                    value=existing_skills['databases'] if existing_skills else "",
                    placeholder="Ex: MySQL, MongoDB, PostgreSQL"
                )
                tools = st.text_input(
                    "Developer Tools", 
                    value=existing_skills['tools'] if existing_skills else "",
                    placeholder="Ex: Git, VS Code, Postman, Docker"
                )
                networking = st.text_input(
                    "Networking Fundamentals (optionnel)", 
                    value=existing_skills['networking'] if existing_skills else "",
                    placeholder="Ex: TCP/IP, HTTP, DNS"
                )
                
                st.markdown("**Soft Skills**")
                soft_skills = st.text_input(
                    "Soft Skills (séparés par des virgules)", 
                    value=existing_skills['soft_skills'] if existing_skills else "",
                    placeholder="Ex: Team Collaboration, Self-Learning, Problem Solving"
                )
                
                if st.form_submit_button("💾 Enregistrer les compétences", width="stretch"):
                    st.session_state.cv_skills = {
                        'languages': languages,
                        'technologies': technologies,
                        'databases': databases,
                        'tools': tools,
                        'networking': networking,
                        'soft_skills': soft_skills
                    }
                    st.success("✅ Compétences enregistrées!")
        
        # TAB 6: Langues
        with tab6:
            st.subheader("Langues")
            
            # Load existing langues
            existing_langues = existing_data['langues']
            if existing_langues and st.session_state.cv_langues_count == 1:
                st.session_state.cv_langues_count = len(existing_langues)
            
            langues_entries = []
            
            for i in range(st.session_state.cv_langues_count):
                col1, col2 = st.columns([1, 1])
                existing_lang = existing_langues[i] if i < len(existing_langues) else None
                
                with col1:
                    langue = st.text_input(
                        f"Langue #{i+1}", 
                        key=f"lang_langue_{i}",
                        value=existing_lang['langue'] if existing_lang else "",
                        placeholder="Ex: Arabe"
                    )
                with col2:
                    niveau = st.selectbox(
                        f"Niveau #{i+1}", 
                        key=f"lang_niveau_{i}",
                        options=["", "Langue maternelle", "Courant", "Intermédiaire", "Débutant"],
                        index=["", "Langue maternelle", "Courant", "Intermédiaire", "Débutant"].index(existing_lang['niveau']) if existing_lang and existing_lang['niveau'] in ["", "Langue maternelle", "Courant", "Intermédiaire", "Débutant"] else 0
                    )
                
                if langue and niveau:
                    langues_entries.append({
                        'langue': langue,
                        'niveau': niveau
                    })
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("➕ Ajouter une langue", width="stretch"):
                    st.session_state.cv_langues_count += 1
                    st.rerun()
            with col2:
                if st.button("💾 Enregistrer les langues", width="stretch", type="primary"):
                    st.session_state.cv_langues = langues_entries
                    st.success("✅ Langues enregistrées!")
        
        # Action buttons at the bottom
        st.markdown("---")
        st.subheader("🎬 Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Enregistrer toutes les données", width="stretch", type="secondary"):
                # Save all data to database
                try:
                    # Get data from session state or forms
                    coordonnees = st.session_state.get('cv_coordonnees', {})
                    
                    if not coordonnees or not coordonnees.get('nom_complet'):
                        st.error("⚠️ Veuillez d'abord remplir vos coordonnées!")
                    else:
                        # Save coordonnees
                        db.save_cv_coordonnees(
                            st.session_state['user_id'],
                            coordonnees.get('nom_complet', ''),
                            coordonnees.get('email', ''),
                            coordonnees.get('telephone', ''),
                            coordonnees.get('ville_region', ''),
                            coordonnees.get('profil', '')
                        )
                        
                        # Save education
                        education = st.session_state.get('cv_education', [])
                        if education:
                            db.save_cv_education(st.session_state['user_id'], education)
                        
                        # Save experience
                        experience = st.session_state.get('cv_experience', [])
                        if experience:
                            db.save_cv_experience(st.session_state['user_id'], experience)
                        
                        # Save skills
                        skills = st.session_state.get('cv_skills', {})
                        if skills:
                            db.save_cv_skills(
                                st.session_state['user_id'],
                                skills.get('languages', ''),
                                skills.get('technologies', ''),
                                skills.get('databases', ''),
                                skills.get('tools', ''),
                                skills.get('networking', ''),
                                skills.get('soft_skills', '')
                            )
                        
                        # Save langues
                        langues = st.session_state.get('cv_langues', [])
                        if langues:
                            db.save_cv_langues(st.session_state['user_id'], langues)
                        
                        st.success("✅ Toutes vos données ont été enregistrées dans la base de données!")
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'enregistrement: {str(e)}")
        
        with col2:
            if st.button("📥 Générer et télécharger mon CV", width="stretch", type="primary"):
                try:
                    from services.cv_generator_service import generate_candidate_cv
                    
                    # Generate CV
                    cv_data_raw = db.get_complete_cv_data(st.session_state['user_id'])
                    
                    if not cv_data_raw['coordonnees']:
                        st.error("⚠️ Veuillez d'abord remplir et enregistrer vos coordonnées!")
                    else:
                        nom_complet = cv_data_raw['coordonnees']['nom_complet']
                        cv_path = generate_candidate_cv(st.session_state['user_id'], nom_complet)
                        
                        if cv_path and os.path.exists(cv_path):
                            with open(cv_path, 'rb') as f:
                                pdf_data = f.read()
                            
                            st.download_button(
                                label="📄 Télécharger mon CV",
                                data=pdf_data,
                                file_name=f"CV_{nom_complet.replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True
                            )
                            st.success("✅ CV généré avec succès!")
                        else:
                            st.error("❌ Erreur lors de la génération du CV")
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

