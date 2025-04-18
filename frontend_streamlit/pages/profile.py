import streamlit as st

from manage_user import get_user_data, update_user, \
    check_authentity, check_if_valid_token

st.title("Profil")

check_token = check_if_valid_token(st.session_state.token)

if check_token:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    user = get_user_data(headers=headers)

    st.text(f"Nom : {user.get("nom")}")
    st.text(f"Email : {user.get("email")}")


    if st.session_state.edit_profile == False:
        if st.button("Modifier le profil"):
            st.session_state.edit_profile = True

    else:
        st.subheader("Modifier le profil")

        new_nom = st.text_input("Nom", value=user.get("nom"))
        new_email = st.text_input("Email", value=user.get("email"))
        new_pswd = st.text_input("Mot de passe", type="password")
        if st.button("Modifier"):
            if not new_nom or not new_email or not new_pswd:
                st.error("❌ Tous les champs sont obligatoires.")
            else:
                response = update_user(new_nom, new_email, new_pswd)
                st.session_state.nom = new_nom
                token = check_authentity(new_nom, new_pswd)
                st.session_state.token = token
                st.session_state.edit_profile = False
                st.rerun()

    if st.button("Déconnexion"):
        st.session_state.pswd_check = False
        st.session_state.token = None
        st.switch_page("app.py")

else:
    st.error("Veuillez vous connecter.")
