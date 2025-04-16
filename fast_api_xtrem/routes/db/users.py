"""
Routes for user management.

Ce module définit les routes FastAPI pour la gestion des utilisateurs,
y compris l'authentification, l'ajout, la mise à jour, la récupération
et la suppression des utilisateurs dans la base de données.
"""

import hashlib
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr, EmailStr
from sqlalchemy.orm import Session

from fast_api_xtrem.db.db_manager import DBManager
from fast_api_xtrem.db.models.user import User
from fast_api_xtrem.logger.logger_manager import LoggerManager


# Initialisation du routeur et du logger
router_users = APIRouter()
db_get = DBManager("sqlite:///database/app_data.db")
db_get.connect()
logger = LoggerManager()


def create_response(
    message: str, status_code: int, data: Optional[Any] = None
) -> JSONResponse:
    """
    Crée une réponse JSON standardisée.

    Args:
        message (str): Message à inclure dans la réponse.
        status_code (int): Code HTTP de la réponse.
        data (Optional[Any]): Données optionnelles à inclure dans la réponse.

    Returns:
        JSONResponse: Réponse JSON standardisée.
    """
    content = {"message": message}
    if data is not None:
        content["data"] = data
    return JSONResponse(content=content, status_code=status_code)


def hash_password(password: str) -> str:
    """
    Hash un mot de passe en utilisant SHA-256.

    Args:
        password (str): Mot de passe en clair.

    Returns:
        str: Mot de passe haché.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_by_name(db: Session, nom: str) -> Optional[User]:
    """
    Récupère un utilisateur par son nom dans la base de données.

    Args:
        db (Session) : Session SQLAlchemy pour interagir
        avec la base de données.
        nom (str) : Nom de l'utilisateur à rechercher.

    Returns:
        Optional[User] : Instance de l'utilisateur trouvé
        ou None si non trouvé.
    """
    return db.query(User).filter_by(nom=nom).first()


class UserLogin(BaseModel):
    """
    Modèle Pydantic pour la connexion d'un utilisateur.

    Attributes :
        nom (str) : Nom de l'utilisateur (1 à 50 caractères).
        pswd (str) : Mot de passe de l'utilisateur (minimum 8 caractères).
    """
    nom: constr(min_length=1, max_length=50)
    pswd: constr(min_length=8)


class UserCreate(BaseModel):
    """
    Modèle Pydantic pour la création d'un utilisateur.

    Attributes :
        nom (str) : Nom de l'utilisateur (1 à 50 caractères).
        email (EmailStr) : Adresse e-mail valide de l'utilisateur.
        pswd (str) : Mot de passe de l'utilisateur (minimum 8 caractères).
    """
    nom: constr(min_length=1, max_length=50)
    email: EmailStr
    pswd: constr(min_length=8)


class UserUpdate(BaseModel):
    """
    Modèle Pydantic pour la mise à jour d'un utilisateur.

    Attributes :
        nom (str) : Nouveau nom de l'utilisateur (1 à 50 caractères).
        email (EmailStr) : Nouvelle adresse e-mail valide de l'utilisateur.
        pswd (str) : Nouveau mot de passe de l'utilisateur
        (minimum 8 caractères).
    """
    nom: constr(min_length=1, max_length=50)
    email: EmailStr
    pswd: constr(min_length=8)


@router_users.post("/login", response_model=dict)
async def login(
        data: UserLogin,
        db: Session = Depends(db_get.get_db)) -> JSONResponse:
    """
    Route pour l'authentification d'un utilisateur.

    Args:
        data (UserLogin) : Données de connexion de l'utilisateur.
            - nom (str) : Nom de l'utilisateur (1 à 50 caractères).
            - pswd (str) : Mot de passe de l'utilisateur
            (minimum 8 caractères).
        db (Session) : Session SQLAlchemy pour interagir
        avec la base de données.

    Returns:
        JSONResponse : Réponse JSON indiquant le succès
        ou l'échec de l'authentification.

    Raises :
        HTTPException :
            - 404 Not Found si l'utilisateur n'est pas trouvé.
            - 401 Unauthorized si les identifiants sont incorrects.
    """
    user = get_user_by_name(db, data.nom)

    if not user:
        db_get.disconnect()
        logger.error(f"Utilisateur {data.nom} non trouvé")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur : utilisateur non trouvé",
        )

    if user.pswd == hash_password(data.pswd):
        db_get.disconnect()
        logger.success(f"Utilisateur {data.nom} authentifié")
        return create_response(
            message="Succès : utilisateur authentifié",
            status_code=status.HTTP_200_OK,
        )

    db_get.disconnect()
    logger.error(f"Utilisateur {data.nom} ou mot de passe incorrect")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Erreur : utilisateur ou mot de passe incorrect",
    )


@router_users.post("/logout", response_model=dict)
async def logout() -> JSONResponse:
    """
    Route pour la déconnexion d'un utilisateur.

    Returns:
        JSONResponse : Réponse JSON indiquant le succès de la déconnexion.
    """
    logger.info("Déconnexion")
    return create_response(
        "Succès : déconnexion réussie", status.HTTP_200_OK)


@router_users.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=dict)
async def add_user(
        data: UserCreate,
        db: Session = Depends(db_get.get_db)) -> JSONResponse:
    """
    Route pour ajouter un nouvel utilisateur dans la base de données.

    Args:
        data (UserCreate) : Données du nouvel utilisateur.
            - nom (str) : Nom de l'utilisateur (1 à 50 caractères).
            - email (EmailStr) : Adresse e-mail valide de l'utilisateur.
            - pswd (str) : Mot de passe de l'utilisateur
            (minimum 8 caractères).
        db (Session) : Session SQLAlchemy pour interagir
        avec la base de données.

    Returns:
        JSONResponse : Réponse JSON indiquant le succès de l'ajout.

    Raises :
        HTTPException : Si le nom d'utilisateur existe déjà.
    """
    if get_user_by_name(db, data.nom):
        db_get.disconnect()
        logger.error(f"Nom d'utilisateur {data.nom} existant")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erreur : nom d'utilisateur déjà existant",
        )

    db_user = User(
        nom=data.nom,
        email=data.email,
        pswd=hash_password(data.pswd),
    )
    db.add(db_user)
    db.commit()
    db_get.disconnect()
    logger.success(f"Utilisateur {data.nom}, {data.email} ajouté")
    return create_response(
        message="Succès : nouvel utilisateur enregistré",
        status_code=status.HTTP_201_CREATED,
        data={"nom": db_user.nom, "email": db_user.email},
    )


@router_users.get("/users", response_model=dict)
async def get_all_users(db: Session = Depends(db_get.get_db)) -> JSONResponse:
    """
    Route pour récupérer tous les utilisateurs de la base de données.

    Args:
        db (Session) : Session SQLAlchemy pour interagir
        avec la base de données.

    Returns:
        JSONResponse : Réponse JSON contenant la liste des utilisateurs.

    Raises :
        HTTPException : Si aucun utilisateur n'est trouvé.
    """
    users = db.query(User).all()

    if not users:
        db_get.disconnect()
        logger.error("Aucun utilisateur trouvé")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur : aucun utilisateur trouvé",
        )

    user_list = [{"nom": user.nom, "email": user.email} for user in users]
    db_get.disconnect()
    logger.success("Tous les utilisateurs trouvés")
    return create_response("Succès", status.HTTP_200_OK, user_list)


@router_users.put("/users/{nom}", response_model=dict)
async def update_user(
    nom: str, data: UserUpdate, db: Session = Depends(db_get.get_db)
) -> JSONResponse:
    """
    Route pour mettre à jour les données d'un utilisateur.

    Args:
        nom (str) : Nom de l'utilisateur à mettre à jour.
        data (UserUpdate) : Nouvelles données de l'utilisateur.
            - nom (str) : Nouveau nom de l'utilisateur (1 à 50 caractères).
            - email (EmailStr) : Nouvelle adresse e-mail
            valide de l'utilisateur.
            - pswd (str) : Nouveau mot de passe de l'utilisateur
            (minimum 8 caractères).
        db (Session) : Session SQLAlchemy pour interagir
        avec la base de données.

    Returns:
        JSONResponse : Réponse JSON indiquant le succès de la mise à jour.

    Raises :
        HTTPException :
            - 404 Not Found si l'utilisateur n'est pas trouvé.
            - 400 Bad Request si les données ne correspondent pas.
    """
    user = get_user_by_name(db, nom)
    if not user:
        db_get.disconnect()
        logger.error("Aucun utilisateur trouvé")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur : aucun utilisateur trouvé",
        )
    if nom != data.nom:
        db_get.disconnect()
        logger.error("Le nom d'utilisateur dans le chemin ne correspond pas")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Erreur : le nom d'utilisateur "
                "dans le chemin ne correspond pas "
                "au nom d'utilisateur dans les données"
            ),
        )
    user.email = data.email
    user.pswd = hash_password(data.pswd)
    db.commit()
    db_get.disconnect()
    logger.success(f"Utilisateur {data.nom} mis à jour")
    return create_response(
        "Succès : mise à jour réussie",
        status.HTTP_200_OK)


@router_users.delete("/users/{nom}", response_model=dict)
async def delete_user(
        nom: str,
        db: Session = Depends(db_get.get_db)) -> JSONResponse:
    """
    Route pour supprimer un utilisateur de la base de données.

    Args:
        nom (str) : Nom de l'utilisateur à supprimer.
        db (Session) : Session SQLAlchemy pour interagir
        avec la base de données.

    Returns:
        JSONResponse : Réponse JSON indiquant le succès de la suppression.

    Raises :
        HTTPException : Si l'utilisateur n'est pas trouvé.
    """
    user = get_user_by_name(db, nom)

    if not user:
        db_get.disconnect()
        logger.error("Aucun utilisateur trouvé")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur : aucun utilisateur trouvé",
        )

    db.delete(user)
    db.commit()
    db_get.disconnect()
    logger.success(f"Utilisateur {nom} supprimé")
    return create_response(
        "Succès : utilisateur supprimé",
        status.HTTP_200_OK)
