import streamlit as st
import logging
from manage_user import check_authentity, \
    user_exist, create_user, check_pswd_security_level, \
    email_exist, update_pswd, check_email_valid
# --- Setup logging ---
logging.basicConfig(level=logging.INFO)

# --- Initialiser session_state si besoin ---
for key, default in {
    "pswd_check": False,
    "reset_password": False,
    "button_pressed": False,
    "email": "",
    "code": "",
}.items():
    st.session_state.setdefault(key, default)

st.title("🔐 Connexion / Inscription")

# --- AUTHENTIFICATION ---
if not st.session_state.pswd_check:
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    # ----- CONNEXION -----
    with tab1:
        if not st.session_state.reset_password:
            st.subheader("Connexion")
            username = st.text_input("Nom d'utilisateur",
                                     key="login_username")
            if username:
                password = st.text_input("Mot de passe",
                                         type="password", key="login_password")
                if password:
                    if user_exist(username):
                        if check_authentity(username, password):
                            st.success("Connexion réussie ✅")
                            st.session_state.pswd_check = True
                            st.rerun()
                        else:
                            st.error("Mot de passe incorrect.")
                            if st.button("Mot de passe oublié ?"):
                                st.session_state.reset_password = True
                                st.session_state.email = ""
                                st.rerun()
                    else:
                        st.error("Nom d'utilisateur inconnu.")

        # ----- RÉINITIALISATION MOT DE PASSE -----
        else:
            st.subheader("🔄 Réinitialisation du mot de passe")
            email = st.text_input("Email",
                                  value=st.session_state.get("email", ""))
            if email:
                if email_exist(email):
                    st.session_state["email"] = email
                    # Remplace par ton vrai système
                    st.session_state["code"] = "123456"
                    st.success("Code envoyé à votre email.")
                    code_input = st.text_input("Entrez le code reçu")
                    if code_input == st.session_state["code"]:
                        new_password = st.text_input("Nouveau mot de passe",
                                                     type="password")
                        if new_password:
                            if check_pswd_security_level(new_password) < 3\
                                    or len(new_password) < 8:
                                st.warning("Mot de passe trop faible.")
                            else:
                                update_pswd(new_password, email)
                                st.success("Mot de passe mis à\
                                            jour avec succès !")
                                if st.button("Retour à la connexion"):
                                    st.session_state.reset_password = False
                                    st.session_state.button_pressed = False
                                    st.rerun()
                    elif code_input != "":
                        st.error("Code incorrect.")
                else:
                    st.error("Email inconnu.")

    # ----- INSCRIPTION -----
    with tab2:
        st.subheader("Créer un compte")
        email = st.text_input("Email", key="signup_email")
        if email:
            if email_exist(email):
                st.error("Email déjà utilisé.")
            else:
                if check_email_valid(email):
                    username = st.text_input("Nom d'utilisateur",
                                             key="signup_username")
                    if username:
                        if user_exist(username):
                            st.error("Nom d'utilisateur déjà utilisé.")
                        else:
                            password = st.text_input("Mot de passe",
                                                     type="password",
                                                     key="signup_password")
                            if password:
                                if check_pswd_security_level(password) < 3\
                                        or len(password) < 8:
                                    st.warning("Mot de passe trop faible.\n\
                                        Au moins 8 caractere dont 1 chiffre\
                                         et un spécial")
                                else:
                                    create_user(username, password, email)
                                    st.success("Compte créé avec succès 🎉")
                                    st.balloons()
                else:
                    st.error("Email non valide")

# --- SI CONNECTÉ ---
else:
    st.success("Connecté avec succès.")
    st.write("➡️ Utilisez le menu à gauche pour accéder aux autres pages.")
    if st.button("Déconnexion"):
        st.session_state.pswd_check = False
        st.rerun()
