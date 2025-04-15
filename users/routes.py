from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from models.user import UtilisateurBase, Utilisateur
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

            utilisateur = db.query(Utilisateur).filter_by(nom=nom).first()

            if utilisateur:
                encoded_password = utilisateur.pswd.encode()
                if (
                    utilisateur.nom == nom and
                    encoded_password == hashlib.sha256(
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


@router.post("/add-user")
async def add_user(data: UtilisateurBase, db: Session = Depends(get_db)):
    """
    Route pour l'ajout d'un utilisateur dans la bdd

    Paramètres :
        - data: les informations envoyées par l'utilisateur
        - db: la session de bdd actuelle
    """
    try:
        if data:
            connect()

            utilisateur = db.query(Utilisateur).filter_by(nom=data.nom).first()

            if utilisateur:
                return JSONResponse(
                    content={
                        "message": "Erreur : nom d'utilisateur déjà existant"
                        }
                    ), 403
            
            hashed_pswd = hashlib.sha256(data.pswd.encode()).hexdigest()

            db_utilisateur = Utilisateur(
                nom = data.nom,
                email = data.email,
                pswd = hashed_pswd
            )

            db.add(db_utilisateur)
            db.commit()

            return JSONResponse(
                content={
                    "message": "Succès : nouvel utilisateur enregistré"
                    }
                ), 200
            
    except Exception as e:
        return JSONResponse(content={"message": "Erreur : " + str(e)}), 500
    
    finally:
        diconnect(db)
