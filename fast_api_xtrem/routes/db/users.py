import hashlib

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from fast_api_xtrem.db.models.user import User
from fast_api_xtrem.main import app

router_users = APIRouter()


###########
# Routes
###########
@router_users.post("/login")
async def login(data, db: Session = Depends(app.services.db_manager.get_db)):
    """
    Route pour l'authentification
    """
    try:
        if data:
            nom = data.nom
            pswd = data.pswd

            user = db.query(User).filter_by(nom=nom).first()  # Use User model

            if user:
                encoded_password = user.pswd.encode()
                if (
                    user.nom == nom and
                    encoded_password ==
                        hashlib.sha256(pswd.encode()).hexdigest()
                ):
                    return JSONResponse(
                        content=
                        {"message":"Succès : utilisateur authentifié"},
                        status_code=200)

                return JSONResponse(
                    content=
                    {"message":
                         "Erreur : utilisateur ou mot de passe incorrect"},
                    status_code=401)

            return JSONResponse(content={"message":"Erreur : "
                                             "utilisateur non trouvé"},
                                status_code=404)

        return JSONResponse(
            content={"message":"Erreur : aucunes données envoyées"},
            status_code=400)

    except Exception as e:
        return JSONResponse(content={"message":"Erreur : " + str(e)},
                            status_code=500)


@router_users.post("/logout")
async def logout():
    """
    Route pour la déconnexion
    """
    # Here you can implement logic to invalidate the user's session or token
    # For example, if using JWT,
    # you could blacklist the token or inform the client to delete it.

    return JSONResponse(content={"message":"Succès : déconnexion réussie"},
                        status_code=200)


@router_users.post("/add-user")
async def add_user(data: User,
                   db: Session = Depends(app.services.db_manager.get_db)):
    """
    Route pour l'ajout d'un utilisateur dans la bdd
    """
    try:
        if data:
            user = db.query(User).filter_by(nom=data.nom).first()

            if user:
                return JSONResponse(
                    content={"message":
                                 "Erreur : nom d'utilisateur déjà existant"},
                    status_code=403)

            hashed_pswd = hashlib.sha256(data.pswd.encode()).hexdigest()

            db_user = User(nom=data.nom, email=data.email, pswd=hashed_pswd)

            db.add(db_user)
            db.commit()

            return JSONResponse(
                content={"message": "Succès : nouvel utilisateur enregistré"},
                status_code=200)

        return JSONResponse(
            content={"message": "Erreur : aucunes données envoyées"},
            status_code=400)

    except Exception as e:
        return JSONResponse(content={"message": "Erreur : " + str(e)},
                            status_code=500)


@router_users.get("/get-all-users")
async def get_all_users(db: Session = Depends(app.services.db_manager.get_db)):
    """
    Route pour récupérer tous les utilisateurs de la bdd
    """
    try:
        users = db.query(User).all()  # Use User model

        if users:
            user_list = [
                {"nom": user.nom,
                 "email": user.email,
                 "pswd": user.pswd} for user in users]

            return JSONResponse(
                content={"data": user_list, "message": "Succès"},
                status_code=200)

        return JSONResponse(
            content={"message": "Erreur : aucun utilisateur trouvé"},
            status_code=404)

    except Exception as e:
        return JSONResponse(content={"message": "Erreur : " + str(e)},
                            status_code=500)


@router_users.post("/update-user")
async def update_user(data: User,
                      db: Session = Depends(app.services.db_manager.get_db)):
    """
    Route pour mettre à jour les données d'un utilisateur
    """
    try:
        if data:
            user = db.query(User).filter_by(nom=data.nom).first()

            if user:
                hashed_pswd = hashlib.sha256(data.pswd.encode()).hexdigest()

                user.nom = data.nom
                user.email = data.email
                user.pswd = hashed_pswd

                db.commit()

                return JSONResponse(
                    content={"message": "Succès : mise à jour réussie"},
                    status_code=200)

            return JSONResponse(
                content={"message": "Erreur : aucun utilisateur trouvé"},
                status_code=404)

        return JSONResponse(
            content={"message": "Erreur : aucunes données envoyées"},
            status_code=400)

    except Exception as e:
        return JSONResponse(
            content={"message": "Erreur : " + str(e)}, status_code=500)


@router_users.post("/delete-user")
async def delete_user(data: User,
                      db: Session = Depends(app.services.db_manager.get_db)):
    """
    Route pour supprimer un utilisateur de la bdd
    """
    try:
        if data:
            user = db.query(User).filter_by(nom=data.nom).first()

            if user:
                db.query(User).filter_by(nom=data.nom).delete()
                db.commit()

                return JSONResponse(
                    content={"message": "Succès : utilisateur supprimé"},
                    status_code=200)

            return JSONResponse(
                content={"message": "Erreur : aucun utilisateur trouvé"},
                status_code=404)

        return JSONResponse(
            content={"message": "Erreur : aucunes données envoyées"},
            status_code=400)

    except Exception as e:
        return JSONResponse(content={"message": "Erreur : " + str(e)},
                            status_code=500)
