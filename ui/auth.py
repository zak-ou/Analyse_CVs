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
                email = st.text_input("Email")
                password = st.text_input("Mot de passe", type="password")
                role = st.radio("Je suis :", ["Candidat", "Recruteur"], horizontal=True)
                submit = st.form_submit_button("Connexion", use_container_width=True)
                
                if submit:
                    user = db.verify_user(email, password, role)
                    if user:
                        # User is a sqlite3.Row object
                        st.success(f"Bienvenue {user['prenom']} {user['nom']} !")
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = user['id']
                        st.session_state['username'] = f"{user['prenom']} {user['nom']}"
                        st.session_state['role'] = role
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects.")

        # REGISTER
        with tab2:
            st.warning("⚠️ Attention : Les comptes existants (ancienne version) ne sont plus valides.")
            role_choice = st.radio("S'inscrire en tant que :", ["Candidat", "Recruteur"], key="reg_role_choice", horizontal=True)
            
            with st.form("register_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    nom = st.text_input("Nom")
                with col_b:
                    prenom = st.text_input("Prénom")
                
                email = st.text_input("Email")
                num_tele = st.text_input("Numéro de Téléphone")
                password = st.text_input("Mot de passe", type="password")
                
                # Fields specific to role
                extra_data = {}
                if role_choice == "Candidat":
                    age = st.number_input("Age", min_value=16, max_value=100, step=1)
                    diplome = st.selectbox("Niveau de Diplôme", ["Bac", "Bac+2", "Bac+3", "Bac+5", "Doctorat", "Autre"])
                    extra_data['age'] = age
                    extra_data['niveau_diplome'] = diplome
                else:
                    domaine = st.text_input("Domaine / Entreprise")
                    extra_data['domaine'] = domaine

                submit_reg = st.form_submit_button("Créer un compte", use_container_width=True)
                
                if submit_reg:
                    if nom and prenom and email and password:
                        if db.create_user(nom, prenom, email, password, role_choice, num_tele=num_tele, **extra_data):
                            st.success("Compte créé avec succès ! Connectez-vous.")
                        else:
                            st.error("Cet email existe déjà ou une erreur est survenue.")
                    else:
                        st.warning("Veuillez remplir tous les champs obligatoires.")
