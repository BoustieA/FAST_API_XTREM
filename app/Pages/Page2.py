import streamlit as st

if not st.session_state.get("pswd_check", False):
    st.warning("Veuillez vous connecter depuis la page d'accueil.")
    st.stop()

st.title("page 2 TODO")
if st.button("deconnection ?"):
    st.session_state.pswd_check = False
    st.rerun()