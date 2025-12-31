import streamlit as st
import database as db
from ui.auth import render_auth
from ui.candidate_space import render_candidate_space
from ui.recruiter_space import render_recruiter_space
from ui.styles import load_css
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="Recruitment System", layout="wide", page_icon="✨")

def main():
    # Initialize DB
    db.init_db()
    load_css() # Load custom CSS from styles.py

    # Session State Initialization
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['role'] = None

    # Routing Logic
    if not st.session_state['logged_in']:
        render_auth()
    else:
        # Sidebar Header & Profile
        with st.sidebar:
            st.markdown(f"""
            <h1 style='color: #6C5CE7; font-size: 1.4rem; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;'>
                 Smart Recruiter 🦄
            </h1>
            <div class="sidebar-profile">
                <div class="sidebar-avatar">{st.session_state['username'][0].upper()}</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: #2D3436; font-size: 0.9rem;">{st.session_state['username']}</div>
                    <div style="color: #636E72; font-size: 0.75rem;">{st.session_state['role']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Spacer for Navigation (which comes from role renderers)
            st.write("")

        # Render Space based on role (This injects the Navigation Radio in the middle)
        if st.session_state['role'] == "Candidat":
            render_candidate_space()
        elif st.session_state['role'] == "Recruteur":
            render_recruiter_space()
        else:
            st.error("Rôle inconnu. Veuillez vous reconnecter.")

        # Sidebar Footer (Logout)
        with st.sidebar:
            st.markdown("---")
            st.write("") # Spacer
            if st.button("🚪 Déconnexion", use_container_width=True):
                st.session_state['logged_in'] = False
                st.session_state['role'] = None
                st.rerun()

if __name__ == "__main__":
    main()
