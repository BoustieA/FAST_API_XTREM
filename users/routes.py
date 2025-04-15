from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from ORM import UtilisateurBase, Utilisateur
from sqlalchemy.orm import Session
from db.db_manager import connect, diconnect, get_db
import hashlib
import os


router = APIRouter()


###########
# Routes
###########
@router.post("/login")
async def login(data: UtilisateurBase, db: Session = Depends(get_db)):
    """
    Route pour l'authentification

    Paramètres :
        - data: les identifiants envoyés par l'utilisateur
        - db: la session de bdd actuelle

    Return :
        - Un message de réponse JSON confirmant ou invalidant
          l'authentification
    """
    try:
        if data:
            nom = data.nom
            pswd = data.pswd

            connect()

            utilisateurs = db.query(Utilisateur).filter_by(nom=nom).first()

            if utilisateurs:
                for utilisateur in utilisateurs:
                    decrypted_password = utilisateur.pswd.decode()
                    if (
                        utilisateur.nom == nom and
                        decrypted_password == hashlib.sha256(
                            pswd.encode()
                            ).hexdigest()
                    ):
                        return JSONResponse(
                            content={
                                "message": "Succès : utilisateur authientifié"
                                }
                            ), 200

                return JSONResponse(
                    content={
                        "message":
                        "Erreur : utilisateur ou mot de passe incorrect"
                        }
                    ), 401

            return JSONResponse(
                content={
                    "message": "Erreur : utilisateur non trouvé"
                    }
                ), 404

        return JSONResponse(
            content={
                "message": "Erreur : aucunes données envoyées"
                }
            ), 400

    except Exception as e:
        return JSONResponse(content={"message": "Erreur : " + str(e)}), 500

    finally:
        diconnect(db)


@router.post("/logout")
async def logout():
    """
    Route pour la déconnexion
    """
    os._exit(0)
