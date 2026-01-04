import streamlit as st
import database as db

def render_auth():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔐 Authentification</h2>", unsafe_allow_html=True)
        st.markdown("")
        
        # Toggle between Login and Register
        # Use session state to control the default index, allowing programmatic switching
        if 'auth_mode' not in st.session_state:
            st.session_state['auth_mode'] = "Se connecter"
            
        options = ["Se connecter", "S'inscrire"]
        # Determine index based on state
        idx = options.index(st.session_state['auth_mode']) if st.session_state['auth_mode'] in options else 0
        
        mode = st.radio("Option", options, index=idx, horizontal=True)
        # Update state if user clicks
        st.session_state['auth_mode'] = mode
        
        st.markdown("---")

        # LOGIN
        if mode == "Se connecter":
            with st.form("login_form"):
                # Check for pre-filled email from registration
                default_email = st.session_state.get('login_email', "")
                
                email = st.text_input("Email", value=default_email)
                password = st.text_input("Mot de passe", type="password")
                role = st.radio("Je suis :", ["Candidat", "Recruteur"], horizontal=True)
                submit = st.form_submit_button("Connexion", width="stretch")
                
                if submit:
                    user = db.verify_user(email, password, role)
                    if user:
                        st.success(f"Bienvenue {user['prenom']} {user['nom']} !")
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = user['id']
                        st.session_state['username'] = f"{user['prenom']} {user['nom']}"
                        st.session_state['user_email'] = user['email']
                        st.session_state['role'] = role
                        
                        # Clear temp email
                        if 'login_email' in st.session_state:
                            del st.session_state['login_email']
                            
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects.")

        # REGISTER
        elif mode == "S'inscrire":
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

                submit_reg = st.form_submit_button("Créer un compte", width="stretch")
                
                if submit_reg:
                    if nom and prenom and email and password:
                        if db.create_user(nom, prenom, email, password, role_choice, num_tele=num_tele, **extra_data):
                            st.success("Compte créé avec succès ! Redirection vers la connexion...")
                            # ACTION: Redirect to login with pre-filled email
                            st.session_state['login_email'] = email
                            # Force the mode back to login for next render
                            st.session_state['auth_mode'] = "Se connecter"
                            st.rerun()
                        else:
                            st.error("Cet email existe déjà ou une erreur est survenue.")
                    else:
                        st.warning("Veuillez remplir tous les champs obligatoires.")
