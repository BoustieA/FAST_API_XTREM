def check_authentity(nm_user,pswd):
    return False
def user_exist(name):
    return True
def create_user(name,pswd,mail):
    pass
def email_exist(mail):
    return True
def update_pswd(pswd,mail):
    pass

def check_pswd_security_level(mdp):
    security=0
    security_number=False
    security_minus=False
    security_maj=False
    security_spec=False
    for i in mdp:
        if security_number==False:
            if ord(i)<58 and ord(i)>47:
                security+=1
                security_number=True
        
        if security_minus==False:
            if ord(i)<123 and ord(i)>96:
                security+=1
                security_minus=True
        
        if security_maj==False:
            if ord(i)<91 and ord(i)>64:
                security+=1
                security_maj=True
        
        if security_spec==False:
            if ord(i)<=47 or ord(i)>=58 and ord(i)<=64\
            or ord(i)>=91 and ord(i)<=96\
            or ord(i)>=123:
                security+=1
                security_spec=True
        if security==4:
            break
    return security