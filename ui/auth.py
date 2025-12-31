import streamlit as st
import database as db

def render_auth():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔐 Authentification</h2>", unsafe_allow_html=True)
        st.markdown("")
        
        tab1, tab2 = st.tabs(["Se connecter", "S'inscrire"])

        # LOGIN
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Nom d'utilisateur")
                password = st.text_input("Mot de passe", type="password")
                role = st.radio("Je suis :", ["Candidat", "Recruteur"], horizontal=True)
                submit = st.form_submit_button("Connexion", use_container_width=True)
                
                if submit:
                    table = 'recreteur' if role == 'Recruteur' else 'users'
                    user = db.verify_user(username, password, table)
                    if user:
                        st.success(f"Bienvenue {user[1]} !")
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = user[0]
                        st.session_state['username'] = user[1]
                        st.session_state['role'] = role
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects.")

        # REGISTER
        with tab2:
            with st.form("register_form"):
                new_user = st.text_input("Choisir un nom d'utilisateur")
                new_pass = st.text_input("Choisir un mot de passe", type="password")
                new_role = st.radio("S'inscrire en tant que :", ["Candidat", "Recruteur"], key="reg_role", horizontal=True)
                submit_reg = st.form_submit_button("Créer un compte", use_container_width=True)
                
                if submit_reg:
                    if new_user and new_pass:
                        table = 'recreteur' if new_role == 'Recruteur' else 'users'
                        if db.create_user(new_user, new_pass, table):
                            st.success("Compte créé avec succès ! Connectez-vous.")
                        else:
                            st.error("Ce nom d'utilisateur existe déjà.")
                    else:
                        st.warning("Veuillez remplir tous les champs.")
