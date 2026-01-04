import streamlit as st

def render_home():
    # --- CUSTOM CSS FOR MODERN LANDING PAGE ---
    st.markdown("""
        <style>
        /* General Resets & Fonts handled by styles.py */
        
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
        }

        /* --- HERO SECTION --- */
        .hero-section {
            padding: 8rem 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 2rem;
        }
        
        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 1.5rem;
            color: #2d3436;
        }
        
        .hero-gradient {
            background: linear-gradient(90deg, #6C5CE7 0%, #a29bfe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
            color: #636E72;
            margin-bottom: 2.5rem;
            line-height: 1.6;
            max-width: 90%;
        }
        
        /* --- STATS SECTION --- */
        .stats-container {
            background-color: #FDFDFD;
            border-top: 1px solid #F0F2F5;
            border-bottom: 1px solid #F0F2F5;
            padding: 3rem 0;
            margin: 2rem 0;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 2.5rem;
            font-weight: 800;
            color: #6C5CE7;
            margin-bottom: 0.5rem;
        }
        .stat-label {
            font-size: 1rem;
            color: #636E72;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* --- HOW IT WORKS CARDS --- */
        .step-card {
            background: white;
            padding: 2.5rem 2rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
            transition: all 0.3s ease;
            height: 100%;
            border: 1px solid rgba(0,0,0,0.02);
            position: relative;
            overflow: hidden;
        }
        .step-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 30px rgba(108, 92, 231, 0.12);
            border-color: rgba(108, 92, 231, 0.2);
        }
        .step-number {
            position: absolute;
            top: -15px;
            right: -15px;
            font-size: 6rem;
            font-weight: 900;
            color: rgba(108, 92, 231, 0.05);
            line-height: 1;
        }
        .step-icon {
            font-size: 2.5rem;
            margin-bottom: 1.5rem;
            display: inline-block;
            background: linear-gradient(135deg, rgba(108, 92, 231, 0.1) 0%, rgba(162, 155, 254, 0.1) 100%);
            padding: 1rem;
            border-radius: 12px;
        }
        .step-title {
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #2D3436;
        }
        .step-desc {
            color: #636E72;
            line-height: 1.6;
        }

        /* --- TRUSTED BY --- */
        .trusted-section {
            padding: 3rem 0;
            text-align: center;
            opacity: 0.7;
        }
        .company-logo {
            font-weight: 700;
            color: #B2BEC3;
            font-size: 1.5rem;
            margin: 0 1.5rem;
        }

        /* --- FOOTER --- */
        .footer {
            background-color: #1e1e2e;
            color: white;
            padding: 4rem 2rem 2rem 2rem;
            margin-top: 5rem;
            border-radius: 20px 20px 0 0;
        }
        .footer h3 {
            color: white !important;
            margin-bottom: 1.5rem;
        }
        .footer-link {
            display: block;
            color: #a0aec0;
            text-decoration: none;
            margin-bottom: 0.8rem;
            transition: color 0.2s;
        }
        .footer-link:hover {
            color: #6C5CE7;
        }

        </style>
    """, unsafe_allow_html=True)

    # --- HEADER / NAVBAR ---
    # Simple flex header
    col_logo, col_spacer, col_login = st.columns([2, 5, 2])
    with col_logo:
        st.markdown("<h2 style='margin:0; padding:0; color:#2d3436; display:flex; align-items:center; gap:10px;'><span style='font-size:1.8rem;'>🚀</span> RecrutIQ</h2>", unsafe_allow_html=True)
    with col_login:
        # Align button right
        st.markdown('<div style="display:flex; justify-content:flex-end;">', unsafe_allow_html=True)
        if st.button("Se connecter", key="nav_login"):
            st.session_state['show_auth'] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # --- HERO SECTION ---
    col_hero_text, col_hero_img = st.columns([1.2, 1])

    with col_hero_text:
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True) # Spacer
        st.markdown("""
            <div class="hero-title">
                Le futur du <br>
                <span class="hero-gradient">Recrutement.</span>
            </div>
            <div class="hero-subtitle">
                RecrutIQ utilise l'Intelligence Artificielle pour analyser, trier et connecter les meilleurs talents aux meilleures opportunités en un temps record.
            </div>
        """, unsafe_allow_html=True)
        
        col_cta_1, col_cta_2 = st.columns([1, 1.5])
        with col_cta_1:
            if st.button("Commencer maintenant", type="primary", use_container_width=True):
                st.session_state['show_auth'] = True
                st.rerun()
        with col_cta_2:
             st.button("En savoir plus", use_container_width=True)

    with col_hero_img:
        # Abstract UI Representation
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
                border-radius: 20px;
                padding: 2rem;
                box-shadow: 0 20px 50px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.03);
                position: relative;
                transform: rotate(-2deg);
                margin-top: 1rem;
            ">
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem; align-items:center;">
                    <div style="width:40px; height:40px; border-radius:10px; background:#FFEAA7;"></div>
                    <div style="width:120px; height:10px; background:#F0F2F5; border-radius:5px;"></div>
                </div>
                <div style="background:#F0F2F5; height:150px; border-radius:12px; margin-bottom:1rem; display:flex; align-items:center; justify-content:center; color:#B2BEC3;">
                    CV Analysis UI
                </div>
                <div style="display:flex; gap:10px;">
                    <div style="flex:1; height:8px; background:#6C5CE7; border-radius:4px; opacity:0.2;"></div>
                    <div style="flex:1; height:8px; background:#6C5CE7; border-radius:4px; opacity:0.1;"></div>
                </div>
                <!-- Floating Badge -->
                <div style="
                    position: absolute;
                    bottom: -20px;
                    right: -20px;
                    background: white;
                    padding: 1rem 1.5rem;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    font-weight: 700;
                    color: #2D3436;
                ">
                    <span style="font-size:1.5rem;">✨</span> 98% Match
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- STATS SECTION ---
    st.markdown("""
        <div class="stats-container">
            <div style="display: flex; justify-content: space-around; max-width: 1000px; margin: 0 auto; flex-wrap: wrap; gap: 2rem;">
                <div class="stat-item">
                    <div class="stat-number">500+</div>
                    <div class="stat-label">Candidats</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">50+</div>
                    <div class="stat-label">Entreprises</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">12k</div>
                    <div class="stat-label">CV Analysés</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">24h</div>
                    <div class="stat-label">Temps Moyen</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- HOW IT WORKS ---
    st.markdown("<h2 style='text-align: center; margin-bottom: 3rem;'>Comment ça marche ?</h2>", unsafe_allow_html=True)
    
    col_step1, col_step2, col_step3 = st.columns(3)
    
    with col_step1:
        st.markdown("""
            <div class="step-card">
                <div class="step-number">1</div>
                <span class="step-icon">📤</span>
                <div class="step-title">Déposez votre CV</div>
                <div class="step-desc">
                    Créez votre profil en quelques secondes et téléchargez votre CV. Notre système supporte PDF et Word.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_step2:
        st.markdown("""
            <div class="step-card">
                <div class="step-number">2</div>
                <span class="step-icon">🧠</span>
                <div class="step-title">Analyse IA</div>
                <div class="step-desc">
                    Nos algorithmes extraient vos compétences, expériences et qualitiés pour construire un profil enrichi.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_step3:
        st.markdown("""
            <div class="step-card">
                <div class="step-number">3</div>
                <span class="step-icon">🤝</span>
                <div class="step-title">Matching</div>
                <div class="step-desc">
                    Recevez des offres qui correspondent parfaitement à votre profil ou trouvez le candidat idéal.
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- FOOTER ---
    st.markdown("""
        <div class="footer">
            <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:2rem; max-width:1200px; margin:0 auto;">
                <div style="flex: 2; min-width: 250px;">
                    <h3>🚀 RecrutIQ</h3>
                    <p style="color:#a0aec0; line-height:1.6; max-width: 300px;">
                        La plateforme de référence pour le recrutement intelligent. Simplifiez vos processus RH dès aujourd'hui.
                    </p>
                </div>
                <div style="flex: 1; min-width: 150px;">
                    <h4 style="color:white; margin-bottom:1rem;">Produit</h4>
                    <a href="#" class="footer-link">Fonctionnalités</a>
                    <a href="#" class="footer-link">Tarifs</a>
                    <a href="#" class="footer-link">Entreprises</a>
                </div>
                <div style="flex: 1; min-width: 150px;">
                    <h4 style="color:white; margin-bottom:1rem;">Support</h4>
                    <a href="#" class="footer-link">Centre d'aide</a>
                    <a href="#" class="footer-link">Contact</a>
                    <a href="#" class="footer-link">Légal</a>
                </div>
                <div style="flex: 1; min-width: 150px;">
                    <h4 style="color:white; margin-bottom:1rem;"> Suivez-nous</h4>
                    <a href="#" class="footer-link">LinkedIn</a>
                    <a href="#" class="footer-link">Twitter</a>
                    <a href="#" class="footer-link">Instagram</a>
                </div>
            </div>
            <div style="border-top:1px solid rgba(255,255,255,0.1); margin-top:3rem; padding-top:1.5rem; text-align:center; color:#57606f; font-size:0.9rem;">
                © 2026 RecrutIQ. Fait avec ❤️ pour l'innovation.
            </div>
        </div>
    """, unsafe_allow_html=True)
