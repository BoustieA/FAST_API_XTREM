import requests
from email_validator import validate_email, EmailNotValidError
import streamlit as st


URL_API = "http://127.0.0.1:8000"


def check_email_valid(mail):
    try:
        validate_email(mail)
        return True
    except EmailNotValidError:
        # L’email est invalide
        return False


def check_authentity(nom, pswd):
    json = {"username": nom, "password": pswd}
    response = requests.post(URL_API + "/users/token", data=json).json()

    return response.get("access_token")


def user_exist(nom):
    response = requests.get(URL_API + "/users")
    data = response.json()
    users = data.get("data", [])
    if not users:
        return False
    for user in users:
        if user.get("nom") == nom:
            return True
    return False


def create_user(nom, pswd, mail):
    json = {"nom": nom, "email": mail, "pswd": pswd}
    requests.post(URL_API + "/users", json=json)


def email_exist(mail):
    response = requests.get(URL_API + "/users")
    data = response.json()
    users = data.get("data", [])
    if not users:
        return False
    for user in users:
        if user.get("email") == mail:
            return True
    return False


def update_pswd(pswd, mail):
    response = requests.get(URL_API + "/users")
    data = response.json()
    users = data.get("data", [])
    nom = ""
    for user in users:
        if user.get("email") == mail:
            nom = user.get("nom")
    json = {"nom": nom, "email": mail, "pswd": pswd}
    requests.put(URL_API + "/users" + nom, json=json)


def check_pswd_security_level(mdp):
    security = 0
    security_number = False
    security_minus = False
    security_maj = False
    security_spec = False
    for i in mdp:
        if not security_number:
            if ord(i) < 58 and ord(i) > 47:
                security += 1
                security_number = True

        if not security_minus:
            if ord(i) < 123 and ord(i) > 96:
                security += 1
                security_minus = True

        if not security_maj:
            if ord(i) < 91 and ord(i) > 64:
                security += 1
                security_maj = True

        if not security_spec:
            if ord(i) <= 47 or ord(i) >= 58 and ord(i) <= 64\
                or ord(i) >= 91 and ord(i) <= 96\
                    or ord(i) >= 123:
                security += 1
                security_spec = True
        if security == 4:
            break
    return security


def get_user_data(headers):
    response = requests.get(URL_API + "/users/me", headers=headers)
    data = response.json()

    if data:
        user = data
        return user

    return None


def update_user(nom, email, pswd):
    json = {"nom": nom, "email": email, "pswd": pswd}

    response = requests.put(URL_API + f"/users/{st.session_state.nom}",
                            json=json)

    if response:
        return response.json()

    return None


def check_if_valid_token(token):
    headers = {"Authorization": f"Bearer {token}"}
    if requests.get(URL_API + "/users/me", headers=headers):
        return True

    return False
