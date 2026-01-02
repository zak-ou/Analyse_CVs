import streamlit as st
import database as db
from ui.auth import render_auth
from ui.candidate_space import render_candidate_space
from ui.recruiter_space import render_recruiter_space
from ui.styles import load_css
from app_logic.automation import run_pending_analyses
import os

st.set_page_config(page_title="Recruitment System", layout="wide", page_icon="✨")

def main():
    # Initialize DB
    db.init_db()
    # Run Automation Checks
    run_pending_analyses()
    
    load_css() # Load custom CSS from styles.py

    # Session State Initialization
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['role'] = None

    # Routing Logic
    if not st.session_state['logged_in']:
        render_auth()
    else:
        # 1. Sidebar Top: Logo, Profile Summary & Menu Header
        with st.sidebar:
            st.markdown("""
            <div class="sidebar-logo">
                <span class="sidebar-logo-icon">🚀</span>
                <span class="sidebar-logo-text">RecrutIQ</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="sidebar-profile">
                <div class="sidebar-avatar">{st.session_state['username'][0].upper()}</div>
                <div class="sidebar-info">
                    <div class="sidebar-name">{st.session_state['username']}</div>
                    <div class="sidebar-role">{st.session_state['role']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<p style='font-size: 0.75rem; color: #A0AEC0; font-weight: 600; text-transform: uppercase; margin-bottom: 10px; padding-left: 10px;'>Menu Principal</p>", unsafe_allow_html=True)

        # 2. Render Space based on role (Navigation Menu)
        if st.session_state['role'] == "Candidat":
            render_candidate_space()
        elif st.session_state['role'] == "Recruteur":
            render_recruiter_space()
        else:
            st.error("Rôle inconnu. Veuillez vous reconnecter.")

        # 3. Sidebar Bottom (Logout)
        with st.sidebar:
            st.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)
            if st.button("🚪 Déconnexion", use_container_width=True, type="secondary"):
                st.session_state['logged_in'] = False
                st.session_state['role'] = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
