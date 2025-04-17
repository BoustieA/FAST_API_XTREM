import streamlit as st
from app.manage_user import get_user_data, update_user

user = get_user_data()

st.title("Profil")

st.text("Nom : ", user.nom)
st.text("Email : ", user.email)

if st.button("Modifier le profil"):
    st.session_state.edit_profile = True
    
    if st.session_state.edit_profile:
        st.subheader("Modifier le profil")

        new_nom = st.text_input("Nom", value=user.nom)
        new_email = st.text_input("Email", value=user.email)
        new_pswd = st.text_input("Mot de passe", type="password")
        if st.button("Modifier"):
            update_user(new_nom, new_email, new_pswd)
