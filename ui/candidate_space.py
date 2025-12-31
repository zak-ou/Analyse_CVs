import streamlit as st
import database as db
import os
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
        st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><h3 style='color:#6C5CE7; margin:0;'>👤 Espace Candidat</h3><p style='color:#888;'>{st.session_state['username']}</p></div>", unsafe_allow_html=True)
        
        menu = option_menu(
            menu_title=None,
            options=["Offres d'Emploi", "Mes Candidatures"],
            icons=["briefcase-fill", "file-earmark-check-fill"], 
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
        <h2 style='color:#6C5CE7; margin-bottom:5px;'>{job['title']}</h2>
        <div style='display:flex; gap:15px; color:#666; font-size:14px; margin-bottom:20px;'>
            <span>📅 Date limite : <b>{job['deadline']}</b></span>
            <span>🎓 Expérience min : <b>{job['experience_min']} ans</b></span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📝 Description du poste")
        st.info(job['description'])

        st.markdown("#### 🛠 Compétences requises")
        skills_html = "".join([f"<span class='skill-pill'>{s.strip()}</span>" for s in job['skills_required'].split(',')])
        st.markdown(skills_html, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("#### 🚀 Postuler")
        uploaded_cv = st.file_uploader("Déposez votre CV (PDF uniquement)", type=['pdf'])
        
        if st.button("Envoyer ma candidature", type="primary", use_container_width=True):
            if uploaded_cv:
                # Sauvegarde locale
                upload_dir = "data/uploads"
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, f"{st.session_state['username']}_{uploaded_cv.name}")
                with open(file_path, "wb") as f:
                    f.write(uploaded_cv.getbuffer())
                
                # Sauvegarde BDD
                if db.submit_application(job['id'], st.session_state['user_id'], file_path):
                    st.balloons()
                    st.success("Votre CV a été transmis au recruteur !")
                    # On attend un peu pour que l'utilisateur voie le message
                    import time
                    time.sleep(2)
                    st.rerun()
                else:
                    st.warning("Vous avez déjà postulé à cette offre.")
            else:
                st.error("N'oubliez pas d'ajouter votre CV !")

    # --- 4. CONTENU PRINCIPAL ---
    
    # 📌 ONGLET : OFFRES D'EMPLOI
    if menu == "Offres d'Emploi":
        st.markdown("<h2 style='color:#262730;'>💼 Dernières opportunités</h2>", unsafe_allow_html=True)
        st.caption("Consultez les offres et postulez directement.")
        st.markdown("---")

        jobs = db.get_jobs()
        if not jobs:
            st.info("🔎 Aucune offre disponible pour le moment.")
        else:
            # Création d'une grille propre (2 colonnes)
            cols = st.columns(2) 
            
            for i, job in enumerate(jobs):
                with cols[i % 2]:
                    # LE CŒUR DU DESIGN : Le conteneur sert de carte
                    with st.container(border=True):
                        # 1. Titre
                        st.markdown(f"<div class='job-title'>{job['title']}</div>", unsafe_allow_html=True)
                        
                        # 2. Métadonnées (Icônes et texte gris)
                        st.markdown(f"""
                        <div class='job-meta'>
                            <span>🗓 {job['deadline']}</span>
                            <span>⏳ {job['experience_min']} ans d'exp.</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 3. Description (coupée proprement par CSS)
                        st.markdown(f"<div class='job-desc'>{job['description']}</div>", unsafe_allow_html=True)
                        
                        # 4. Tags de compétences (limités à 3 pour ne pas casser le design)
                        skills = job['skills_required'].split(',')[:3]
                        skills_html = "".join([f"<span class='skill-pill'>{s.strip()}</span>" for s in skills])
                        st.markdown(f"<div style='margin-bottom:15px;'>{skills_html}</div>", unsafe_allow_html=True)
                        
                        # 5. BOUTON INTÉGRÉ (Il est dans le conteneur, donc dans la carte)
                        # 'use_container_width=True' le force à prendre toute la largeur
                        if st.button("Voir l'offre & Postuler", key=f"job_{job['id']}", use_container_width=True):
                            show_job_dialog(job)

   # --- SECTION : MES CANDIDATURES ---
    elif menu == "Mes Candidatures":
        st.title("Suivi des candidatures")
        
        my_apps = db.get_applications_for_candidate(st.session_state['user_id'])
        
        if not my_apps:
            st.info("Vous n'avez pas encore postulé.")
        else:
            # Affichage sous forme de liste propre
            for app in my_apps:
                is_analyzed = app['score'] is not None
                status_class = "status-done" if is_analyzed else "status-pending"
                status_text = "Analysé" if is_analyzed else "En attente"
                score_display = f"{app['score']}/100" if is_analyzed else "--"

                with st.expander(f"{app['job_title']} (Postulé le {app['upload_date']})"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Statut :** <span class='status-badge {status_class}'>{status_text}</span>", unsafe_allow_html=True)
                        st.write(f"**Fichier :** {os.path.basename(app['cv_filepath'])}")
                    
                    with col2:
                        st.metric("Votre Score", score_display)
                    
                    if is_analyzed:
                        st.markdown("---")
                        st.caption("Détails de l'analyse automatique :")
                        # On suppose que 'skills' est stocké dans la BDD ou récupéré
                        if 'skills' in app and app['skills']:
                            st.write(f"**Compétences détectées :** {app['skills']}")