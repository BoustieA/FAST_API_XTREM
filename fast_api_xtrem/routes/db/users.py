"""
Routes for user management.

Ce module définit les routes FastAPI pour la gestion des utilisateurs,
ainsi que l'accès au logger et à la base de données
via les services de l'application.
"""

import hashlib
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy.orm import Session

from fast_api_xtrem.db.models.user import User

router_users = APIRouter()


def get_db(request: Request):
    """
    Dépendance pour récupérer la Session SQLAlchemy
    via le DBManager présent dans app.state.services.
    """
    db_manager = request.app.state.services.db_manager
    yield from db_manager.get_db()


def get_logger(request: Request):
    """
    Dépendance pour récupérer le logger
    exposé dans app.state.logger.
    """
    return request.app.state.logger


def create_response(
    message: str, status_code: int, data: Optional[Any] = None
) -> JSONResponse:
    """
    Crée une réponse JSON standardisée.

    Args:
        message (str): Message de retour.
        status_code (int): Code HTTP à renvoyer.
        data (Optional[Any], optional): Données supplémentaires.
        Par défaut None.

    Returns:
        JSONResponse: La réponse structurée.
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
        str: Mot de passe hashé.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_by_name(db: Session, nom: str) -> Optional[User]:
    """
    Récupère un utilisateur par son nom.

    Args:
        db (Session): Session SQLAlchemy.
        nom (str): Nom de l'utilisateur.

    Returns:
        Optional[User]: L'utilisateur s'il existe, sinon None.
    """
    return db.query(User).filter_by(nom=nom).first()


class UserLogin(BaseModel):
    """
    Modèle de données pour la connexion utilisateur.
    """

    nom: constr(min_length=1, max_length=50)
    pswd: constr(min_length=8)


class UserCreate(BaseModel):
    """
    Modèle de données pour la création d'un utilisateur.
    """

    nom: constr(min_length=1, max_length=50)
    email: EmailStr
    pswd: constr(min_length=8)


class UserUpdate(BaseModel):
    """
    Modèle pour la mise à jour d'un utilisateur.
    Autorise la modification du nom, de l'email et du mot de passe.
    """

    nom: constr(min_length=1, max_length=50)
    email: EmailStr
    pswd: constr(min_length=8)


@router_users.post("/login", response_model=dict)
async def login(
    data: UserLogin, db: Session = Depends(get_db), logger=Depends(get_logger)
) -> JSONResponse:
    """
    Authentifie un utilisateur.

    Args:
        data (UserLogin): Identifiants de connexion.
        db (Session): Session de base de données.
        logger: Logger.

    Returns:
        JSONResponse: Réponse avec message de succès ou erreur.
    """
    user = get_user_by_name(db, data.nom)
    if not user:
        logger.error(f"Utilisateur {data.nom} non trouvé")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur : utilisateur non trouvé",
        )
    if user.pswd == hash_password(data.pswd):
        logger.success(f"Utilisateur {data.nom} authentifié")
        return create_response(
            message="Succès : utilisateur authentifié",
            status_code=status.HTTP_200_OK,
        )
    logger.error(f"Mot de passe incorrect pour utilisateur {data.nom}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Erreur : utilisateur ou mot de passe incorrect",
    )


@router_users.post("/logout", response_model=dict)
async def logout(logger=Depends(get_logger)) -> JSONResponse:
    """
    Déconnecte un utilisateur (statique pour le moment).

    Args:
        logger: Logger.

    Returns:
        JSONResponse: Message de confirmation.
    """
    logger.info("Déconnexion")
    return create_response(
        message="Succès : déconnexion réussie",
        status_code=status.HTTP_200_OK,
    )


@router_users.post(
    "/users", status_code=status.HTTP_201_CREATED, response_model=dict
)
async def add_user(
    data: UserCreate, db: Session = Depends(get_db), logger=Depends(get_logger)
) -> JSONResponse:
    """
    Crée un nouvel utilisateur.

    Args:
        data (UserCreate): Données de l'utilisateur à créer.
        db (Session): Session de base de données.
        logger: Logger.

    Returns:
        JSONResponse: Résultat de la création.
    """
    if get_user_by_name(db, data.nom):
        logger.error(f"Nom d'utilisateur {data.nom} existant")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erreur : nom d'utilisateur déjà existant",
        )
    db_user = User(
        nom=data.nom, email=data.email, pswd=hash_password(data.pswd)
    )
    db.add(db_user)
    db.commit()
    logger.success(f"Utilisateur {data.nom}, {data.email} ajouté")
    return create_response(
        message="Succès : nouvel utilisateur enregistré",
        status_code=status.HTTP_201_CREATED,
        data={"nom": db_user.nom, "email": db_user.email},
    )


@router_users.get("/users", response_model=dict)
async def get_all_users(
    db: Session = Depends(get_db), logger=Depends(get_logger)
) -> JSONResponse:
    """
    Récupère la liste de tous les utilisateurs.

    Args:
        db (Session): Session de base de données.
        logger: Logger.

    Returns:
        JSONResponse: Liste des utilisateurs.
    """
    users = db.query(User).all()
    if not users:
        logger.error("Aucun utilisateur trouvé")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur : aucun utilisateur trouvé",
        )
    user_list = [{"nom": u.nom, "email": u.email} for u in users]
    logger.success("Tous les utilisateurs trouvés")
    return create_response(
        message="Succès",
        status_code=status.HTTP_200_OK,
        data=user_list,
    )


@router_users.put("/users/{nom}", response_model=dict)
async def update_user(
    nom: str,
    data: UserUpdate,
    db: Session = Depends(get_db),
    logger=Depends(get_logger),
) -> JSONResponse:
    """
    Met à jour un utilisateur existant.

    Args:
        nom (str): Nom actuel de l'utilisateur.
        data (UserUpdate): Nouvelles données.
        db (Session): Session base de données.
        logger: Logger.

    Returns:
        JSONResponse: Message de succès ou erreur.
    """
    user = get_user_by_name(db, nom)
    if not user:
        logger.error("Aucun utilisateur trouvé")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur : aucun utilisateur trouvé",
        )
    if data.nom != nom and get_user_by_name(db, data.nom):
        logger.error(f"Nom d'utilisateur {data.nom} déjà utilisé")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erreur : nouveau nom déjà existant",
        )
    user.nom = data.nom
    user.email = data.email
    user.pswd = hash_password(data.pswd)
    db.commit()
    logger.success(f"Utilisateur {nom} mis à jour en {data.nom}")
    return create_response(
        message="Succès : mise à jour réussie",
        status_code=status.HTTP_200_OK,
        data={"nom": user.nom, "email": user.email},
    )


@router_users.delete("/users/{nom}", response_model=dict)
async def delete_user(
    nom: str, db: Session = Depends(get_db), logger=Depends(get_logger)
) -> JSONResponse:
    """
    Supprime un utilisateur existant.

    Args:
        nom (str): Nom de l'utilisateur à supprimer.
        db (Session): Session base de données.
        logger: Logger.

    Returns:
        JSONResponse: Message de confirmation.
    """
    user = get_user_by_name(db, nom)
    if not user:
        logger.error("Aucun utilisateur trouvé")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur : aucun utilisateur trouvé",
        )
    db.delete(user)
    db.commit()
    logger.success(f"Utilisateur {nom} supprimé")
    return create_response(
        message="Succès : utilisateur supprimé",
        status_code=status.HTTP_200_OK,
    )
