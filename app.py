import streamlit as st
import logging

from manage_user import check_authentity, user_exist, create_user,check_pswd_security_level, email_exist, update_pswd

      



if __name__=="__main__":
    #update_tables("nm_user","mdp")
    # Set up logging configuration
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='file_changes.log',
                        filemode='w')
    #configure_logging()
    placeholder1=st.empty()
    placeholder4=st.empty()
    placeholder1.title("Connection")
    # Test logging
    logging.info("Logging is working.")
    if "pswd_check" not in st.session_state:
        st.session_state.pswd_check = False
    if "button_pressed" not in st.session_state:
        st.session_state["button_pressed"]=False
    if "reset_password" not in st.session_state:
        st.session_state["reset_password"]=False
    logging.debug("button_pressed" +str(st.session_state["button_pressed"]))
    if not st.session_state.pswd_check:
        tab1, tab2 = placeholder4.tabs(["Connection","Inscription"])
        with tab1:
            logging.warning("entering tab1")
            placeholder2=st.empty()
            placeholder3=st.empty()
            placeholder_pswd_fail=st.empty()
            placeholder_reset_pswd1=st.empty()
            if not st.session_state["button_pressed"] and not st.session_state["reset_password"]:
                nm_user=placeholder2.text_input("Nom d'utilisateur",key=1)
                if nm_user !="":
                    mdp=placeholder3.text_input("mot de passe",key=2)
                    if user_exist(nm_user):
                        if mdp!="":
                            if check_authentity(nm_user,mdp):
                                st.session_state.pswd_check=True
                                #placeholder2.empty()
                                #placeholder3.empty()
                                #placeholder4.empty()
                                logging.info("connection succesfull")
                                st.rerun()
                            else:
                                placeholder_pswd_fail.text("incorrect")
                                logging.warning("wrong password")
                                if st.session_state["button_pressed"] or placeholder_reset_pswd1.button("pasword forgotten ?"):
                                    st.session_state["button_pressed"]=True
                                    logging.warning("button_pressed "+str(st.session_state["button_pressed"]))
                                    st.rerun()
            elif st.session_state["button_pressed"] and not st.session_state["reset_password"]:
                logging.warning("entering button step")
                placeholder2.empty()
                placeholder3.empty()
                placeholder_pswd_fail.empty()
                placeholder_reset_pswd1.empty()
                ph_mail=st.empty()
                email=ph_mail.text_input("email")
                if email!="":
                    if email_exist(email):
                        st.session_state["reset_password"]=True
                        st.session_state["email"]=email
                        #code=np.random.randint(100000)
                        code=str(1)
                        st.session_state["code"]=code
                        
                        #send_mail()
                        
                        st.rerun()
                    else:
                        st.text("mail inconnu")
                        logging.warning("mail inconnu")
            elif st.session_state["reset_password"]:
                code_placeholder=st.empty()
                succesfull_placeholder=st.empty()
                logging.warning("email sent")
                #ph_mail.empty()
                
                
                code_test=code_placeholder.text_input("saisir le code envoyé à l'adresse mail")
                if code_test==st.session_state["code"]:
                    code_placeholder.empty()
                    
                    mdp=placeholder_reset_pswd1.text_input("nouveau mot de passe")

                    st.session_state["button_pressed"]=False
                    if mdp!="":
                        security_level=check_pswd_security_level(mdp)
                        if security_level<3:
                            st.text("niveau de sécurité insuffisant ajouter caractère spécial, majuscule, chiffre")
                        
                        else:
                            st.text("niveau de sécurité : "+str(security_level))
                            #create_tables()
                            update_pswd(mdp,st.session_state["email"])
                            if succesfull_placeholder.button("Retournerà la page d'acceuil ?"):
                                st.session_state["reset_password"]=False
                                st.rerun()
        with tab2:
            
            ph_mail2=st.empty()
            placeholder6=st.empty()
            placeholder5=st.empty()
            mail = ph_mail2.text_input("email",key=3)
            if mail!="":
                if not email_exist(mail):
                    nm_user=placeholder6.text_input("Nom d'utilisateur",key=4)
                    if nm_user !="":
                        if user_exist(nm_user):
                            st.text("nom_utilisé")
                            logging.warning("attempt to create account with used name")
                        else:  
                            mdp=placeholder5.text_input("mot de passe",key=5)
                            if mdp!="":
                                security_level=check_pswd_security_level(mdp)
                                if security_level<3:
                                    st.text("niveau de sécurité insuffisant ajouter caractère spécial, majuscule, chiffre")
                                
                                else:
                                    st.text("niveau de sécurité : "+str(security_level))
                                    create_user(nm_user,mdp,mail)
                                    placeholder6.empty()
                                    placeholder5.empty()
                                    ph_mail2.empty()
                else:
                    logging.warning("mail already exist")
                    st.text("mail already exist")
    if st.session_state.pswd_check:
        logging.error(str(st.session_state.pswd_check))
        st.session_state['affichage_page']=True
        placeholder1.empty()
        pg = st.navigation([
        st.Page("Pages/Page1.py", title="Connection"),
        st.Page("Pages/Page2.py", title="Déconnection"),
        #st.Page("Pages/page3.py", title="Analyse modèle", icon=":material/manufacturing:"),
        ])
        pg.run()