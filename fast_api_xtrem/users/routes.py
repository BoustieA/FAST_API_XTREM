from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fast_api_xtrem.models.user import UtilisateurBase, Utilisateur
from sqlalchemy.orm import Session
from fast_api_xtrem.main import app
import hashlib
import os


router_users = APIRouter()


###########
# Routes
###########
@router_users.post("/login")
async def login(data: UtilisateurBase,
                db: Session = Depends(app.services.db_manager.get_db)):
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
                            "message": "Succès : utilisateur authentifié"
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


@router_users.post("/logout")
async def logout():
    """
    Route pour la déconnexion
    """
    os._exit(0)


@router_users.post("/add-user")
async def add_user(data: UtilisateurBase,
                   db: Session = Depends(app.services.db_manager.get_db)):
    """
    Route pour l'ajout d'un utilisateur dans la bdd

    Paramètres :
        - data: les informations envoyées par l'utilisateur
        - db: la session de bdd actuelle

    Return :
        - Un message de réponse JSON confirmant ou invalidant l'ajout
    """
    try:
        if data:
            utilisateur = db.query(
                Utilisateur
                ).filter_by(nom=data.nom).first()

            if utilisateur:
                return JSONResponse(
                    content={
                        "message": "Erreur : nom d'utilisateur déjà existant"
                        }
                    ), 403

            hashed_pswd = hashlib.sha256(data.pswd.encode()).hexdigest()

            db_utilisateur = Utilisateur(
                nom=data.nom,
                email=data.email,
                pswd=hashed_pswd
            )

            db.add(db_utilisateur)
            db.commit()

            return JSONResponse(
                content={
                    "message": "Succès : nouvel utilisateur enregistré"
                    }
                ), 200

        return JSONResponse(
            content={
                "message": "Erreur : aucunes données envoyées"
                }
            ), 400

    except Exception as e:
        return JSONResponse(content={"message": "Erreur : " + str(e)}), 500


@router_users.get("/get-all-users")
async def get_all_users(db: Session = Depends(
                                    app.services.db_manager.get_db)):
    """
    Route pour récupérer tous les utilisateurs de la bdd

    Paramètres :
        - db: la session de bdd actuelle

    Return :
        - Une liste contenant toutes les informations des utilisateurs
          en JSON
        - Un message de réponse JSON confirmant ou invalidant la
          récupération des données
    """
    try:
        utilisateurs = db.query(Utilisateur).all()

        if utilisateurs:
            liste_utilisateurs = [
                {
                    "nom": utilisateur.nom,
                    "email": utilisateur.email,
                    "pswd": utilisateur.pswd
                }
                for utilisateur in utilisateurs
            ]

            return JSONResponse(content={
                "data": liste_utilisateurs,
                "message": "Succès"
                }
            ), 200

        return JSONResponse(
            content={
                "message": "Erreur : aucun utilisateur trouvé"
                }
            ), 404

    except Exception as e:
        return JSONResponse(content={"message": "Erreur : " + str(e)}), 500


@router_users.post("/update-user")
async def update_user(data: UtilisateurBase,
                      db: Session = Depends(app.services.db_manager.get_db)):
    """
    Route pour mettre à jour les données d'un utilisateur

    Paramètres :
        - data: les informations envoyées par l'utilisateur
        - db: la session de bdd actuelle

    Return :
        - Un message de réponse JSON confirmant ou invalidant la
          mise à jour des données
    """
    try:
        if data:
            utilisateur = db.query(
                Utilisateur
                ).filter_by(nom=data.nom).first()

            if utilisateur:
                hashed_pswd = hashlib.sha256(data.pswd.encode()).hexdigest()

                utilisateur.nom = data.nom,
                utilisateur.email = data.email,
                utilisateur.pswd = hashed_pswd

                db.commit()

                return JSONResponse(
                    content={
                        "message": "Succès : mise à jour réussie"
                        }
                    ), 200

            return JSONResponse(
                content={
                    "message": "Erreur : aucun utilisateur trouvé"
                    }
                ), 404

        return JSONResponse(
            content={
                "message": "Erreur : aucunes données envoyées"
                }
            ), 400

    except Exception as e:
        return JSONResponse(content={"message": "Erreur : " + str(e)}), 500


@router_users.post("/delete-user")
async def delete_user(data: UtilisateurBase,
                      db: Session = Depends(app.services.db_manager.get_db)):
    """
    Route pour supprimer un utilisateur de la bdd

    Paramètres :
        - db: la session de bdd actuelle

    Return :
        - Un message de réponse JSON confirmant ou invalidant la
          mise à jour des données
    """
    try:
        if data:
            utilisateur = db.query(Utilisateur).filter_by(nom=data.nom).first()

            if utilisateur:
                db.query(Utilisateur).filter_by(nom=data.nom).delete()
                db.commit()

                return JSONResponse(
                    content={
                        "message": "Succès : utilisateur supprimé"
                        }
                    ), 200

            return JSONResponse(
                content={
                    "message": "Erreur : aucun utilisateur trouvé"
                    }
                ), 404

        return JSONResponse(
            content={
                "message": "Erreur : aucunes données envoyées"
                }
            ), 400

    except Exception as e:
        return JSONResponse(content={"message": "Erreur : " + str(e)}), 500
