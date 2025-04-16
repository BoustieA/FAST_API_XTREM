import hashlib
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr, EmailStr
from sqlalchemy.orm import Session

from fast_api_xtrem.db.models.user import User

router_users = APIRouter()


# Fonctions utilitaires
def create_response(message: str, status_code: int,
                    data: Optional[Any] = None) -> JSONResponse:
    """Crée une réponse JSON standard
    avec un message et des données optionnelles"""
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


# Pydantic Models for request validation
class UserLogin(BaseModel):
    nom: constr(min_length=1, max_length=50)
    pswd: constr(min_length=8)  # Consider a minimum password length


class UserCreate(BaseModel):
    nom: constr(min_length=1, max_length=50)
    email: EmailStr
    pswd: constr(min_length=8)


class UserUpdate(BaseModel):
    nom: constr(min_length=1, max_length=50)
    email: EmailStr
    pswd: constr(min_length=8)  # added pswd


# Routes
@router_users.post("/login")
async def login(data: UserLogin, db: Session = Depends(lambda: ...)):
    """Route pour l'authentification"""
    user = get_user_by_name(db, data.nom)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur : utilisateur non trouvé",
        )

    if user.pswd == hash_password(data.pswd):
        return create_response(
            message="Succès : utilisateur authentifié",
            status_code=status.HTTP_200_OK,
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Erreur : utilisateur ou mot de passe incorrect",
    )


@router_users.post("/logout")
async def logout():
    """Route pour la déconnexion"""
    return create_response("Succès : déconnexion réussie",
                           status.HTTP_200_OK)
    #  In most modern web applications,
    #  "logging out" often involves client-side actions (like clearing tokens).
    #  A server-side "/logout" might invalidate
    #  a session, but with token-based auth (common in FastAPI), the server
    #  might not have much to do here.  Consider if you need to do anything
    #  server-side.


@router_users.post("/add_user", status_code=status.HTTP_201_CREATED)
async def add_user(data: UserCreate, db: Session = Depends(lambda: ...)):
    """Route pour l'ajout d'un utilisateur dans la bdd"""
    if get_user_by_name(db, data.nom):
        raise HTTPException(
            # Use 409 Conflict for duplicate resources
            status_code=status.HTTP_409_CONFLICT,
            detail="Erreur : nom d'utilisateur déjà existant",
        )

    db_user = User(
        nom=data.nom,
        email=data.email,
        pswd=hash_password(data.pswd))
    db.add(db_user)
    db.commit()
    return create_response(
        message="Succès : nouvel utilisateur enregistré",
        status_code=status.HTTP_201_CREATED,
        data={"nom": db_user.nom, "email": db_user.email},
    )


@router_users.get("/users")  # Changed endpoint
async def get_all_users(db: Session = Depends(lambda: ...)):
    """Route pour récupérer tous les utilisateurs de la bdd"""
    users = db.query(User).all()

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur : aucun utilisateur trouvé",
        )

    user_list = [{"nom": user.nom, "email": user.email} for user in users]
    return create_response("Succès", status.HTTP_200_OK, user_list)


@router_users.put("/users/{nom}")
async def update_user(
        nom: str,
        data: UserUpdate,
        db: Session = Depends(lambda: ...)):
    """Route pour mettre à jour les données d'un utilisateur"""
    user = get_user_by_name(db, nom)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur : aucun utilisateur trouvé",
        )
    # check if the username in the path matches the username in the body
    if nom != data.nom:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur : le nom d'utilisateur dans le chemin ne "
                   "correspond pas au nom d'utilisateur dans les données",
        )
    user.email = data.email
    user.pswd = hash_password(data.pswd)  # Hash the password.
    db.commit()
    return create_response("Succès : mise à jour réussie",
                           status.HTTP_200_OK)


@router_users.delete("/users/{nom}")
async def delete_user(nom: str, db: Session = Depends(lambda: ...)):
    """Route pour supprimer un utilisateur de la bdd"""
    user = get_user_by_name(db, nom)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur : aucun utilisateur trouvé",
        )

    db.delete(user)
    db.commit()
    return create_response("Succès : utilisateur supprimé",
                           status.HTTP_200_OK)
