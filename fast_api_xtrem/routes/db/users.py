import hashlib
from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from fast_api_xtrem.db.models.user import User
from fast_api_xtrem.main import app

router_users = APIRouter()

# À retirer quand les modèles Pydantic seront implémentés
# Modèles Pydantic pour la validation des données
class UserCreate(BaseModel):
    nom: str
    email: str
    pswd: str


class UserLogin(BaseModel):
    nom: str
    pswd: str


class UserResponse(BaseModel):
    nom: str
    email: str


# Fonctions utilitaires
def create_response(message: str, status_code: int,
                    data: Optional[Any] = None) -> JSONResponse:
    """Crée une réponse JSON standard avec un message et des données optionnelles"""
    content = {"message": message}
    if data is not None:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)


def hash_password(password: str) -> str:
    """Hash le mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_by_name(db: Session, nom: str) -> Optional[User]:
    """Récupère un utilisateur par son nom"""
    return db.query(User).filter_by(nom=nom).first()


def handle_exceptions(func):
    """Décorateur pour gérer les exceptions de manière uniforme"""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            return create_response(f"Erreur : {str(e)}",
                                   500)

    return wrapper


# Routes
@router_users.post("/login")
@handle_exceptions
async def login(data: UserLogin,
                db: Session = Depends(app.services.db_manager.get_db)):
    """Route pour l'authentification"""
    user = get_user_by_name(db, data.nom)

    if not user:
        return create_response("Erreur : utilisateur non trouvé",
                               404)

    if user.pswd == hash_password(data.pswd):
        return create_response("Succès : utilisateur authentifié",
                               200)

    return create_response(
        "Erreur : utilisateur ou mot de passe incorrect",
                           401)


@router_users.post("/logout")
async def logout():
    """Route pour la déconnexion"""
    return create_response("Succès : déconnexion réussie",
                           200)


@router_users.post("/add-user")
@handle_exceptions
async def add_user(data: UserCreate,
                   db: Session = Depends(app.services.db_manager.get_db)):
    """Route pour l'ajout d'un utilisateur dans la bdd"""
    if get_user_by_name(db, data.nom):
        return create_response(
            "Erreur : nom d'utilisateur déjà existant", 403)

    db_user = User(
        nom=data.nom,
        email=data.email,
        pswd=hash_password(data.pswd)
    )

    db.add(db_user)
    db.commit()

    return create_response("Succès : nouvel utilisateur enregistré",
                           200)


@router_users.get("/get-all-users")
@handle_exceptions
async def get_all_users(db: Session = Depends(app.services.db_manager.get_db)):
    """Route pour récupérer tous les utilisateurs de la bdd"""
    users = db.query(User).all()

    if not users:
        return create_response("Erreur : aucun utilisateur trouvé",
                               404)

    user_list = [{"nom": user.nom, "email": user.email, "pswd": user.pswd} for
                 user in users]
    return create_response("Succès", 200, user_list)


@router_users.post("/update-user")
@handle_exceptions
async def update_user(data: UserCreate,
                      db: Session = Depends(app.services.db_manager.get_db)):
    """Route pour mettre à jour les données d'un utilisateur"""
    user = get_user_by_name(db, data.nom)

    if not user:
        return create_response("Erreur : aucun utilisateur trouvé",
                               404)

    user.email = data.email
    user.pswd = hash_password(data.pswd)

    db.commit()

    return create_response("Succès : mise à jour réussie",
                           200)


@router_users.post("/delete-user")
@handle_exceptions
async def delete_user(data: UserLogin,
                      db: Session = Depends(app.services.db_manager.get_db)):
    """Route pour supprimer un utilisateur de la bdd"""
    user = get_user_by_name(db, data.nom)

    if not user:
        return create_response("Erreur : aucun utilisateur trouvé",
                               404)

    db.query(User).filter_by(nom=data.nom).delete()
    db.commit()

    return create_response("Succès : utilisateur supprimé",
                           200)
