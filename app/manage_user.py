import requests


API_adress = "http://127.0.0.1:8000"


def check_authentity(nom, pswd):
    json = {"nom": nom, "pswd": pswd}
    response = requests.post(API_adress + "/login", json=json)
    code = response.status_code
    if code == 200:
        return True
    else:
        return False


def user_exist(nom):
    json = {"nom": nom, "pswd": ""}
    response = requests.post(API_adress + "/login", json=json)
    code = response.status_code
    if code == 401:
        return True
    return False


def create_user(nom, pswd, mail):
    json = {"nom": nom, "email": mail, "pswd": pswd}
    requests.post(API_adress + "/add_user", json=json)


def email_exist(mail):
    json = {"email": mail}
    return requests.post(API_adress + "/mail_exist", json=json)


def update_pswd(pswd, mail):
    json = {"nom": "", "mail": mail, "pswd": ""}
    nom = requests.post(API_adress + "/get_name_from_mail", json=json)
    json = {"nom": nom, "mail": mail, "pswd": pswd}
    requests.post(API_adress + "/update-user", json)


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
