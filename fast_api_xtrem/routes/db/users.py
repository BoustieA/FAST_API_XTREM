"""
Routes pour la gestion des utilisateurs.

Ce module définit les endpoints CRUD pour les utilisateurs,
avec authentification JWT et gestion des dépendances.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from fast_api_xtrem.db.models.user import User, UserCreate, \
    UserLogin, UserUpdate

# Configuration JWT
SECRET_KEY = (
    "votre-cle-secrete"  # À remplacer par une variable d'environnement
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router_users = APIRouter(prefix="/users", tags=["users"])


def get_db(request: Request):
    """
    Dépendance pour récupérer la Session SQLAlchemy
    via le DBManager présent dans fast_api.state.services.
    """
    db_manager = request.app.state.services.db_manager
    yield from db_manager.get_db()


def get_logger(request: Request):
    """
    Dépendance pour récupérer le logger
    exposé dans fast_api.state.logger.
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
    "", status_code=status.HTTP_201_CREATED, response_model=dict
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


@router_users.get("", response_model=dict)
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


@router_users.put("/{nom}", response_model=dict)
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


@router_users.delete("/{nom}")
async def delete_user(
    nom: str, db: Session = Depends(get_db), logger=Depends(get_logger)
) -> JSONResponse:
    """
    Supprime un utilisateur existant.
    """
    user = get_user_by_name(db, nom)
    if not user:
        logger.error(f"Utilisateur {nom} non trouvé")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur : utilisateur non trouvé",
        )

    db.delete(user)
    db.commit()

    logger.success(f"Utilisateur {nom} supprimé")
    return create_response(
        message="Succès : utilisateur supprimé", status_code=status.HTTP_200_OK
    )


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crée un token JWT d'accès.

    Args:
        data (dict): Données à encoder dans le token
        expires_delta (Optional[timedelta]): Durée de validité du token

    Returns:
        str: Token JWT encodé
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, logger=Depends(get_logger)) -> dict:
    """
    Décode et valide un token JWT.

    Args:
        token (str): Token JWT à décoder
        logger: Logger pour le suivi des erreurs

    Returns:
        dict: Payload décodé

    Raises:
        HTTPException: Si le token est invalide ou expiré
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError as exc:
        logger.error("Token non valide")
        raise HTTPException(status_code=401, detail="Token invalide") from exc


@router_users.post("/token")
async def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    logger=Depends(get_logger),
):
    """Route d'authentification qui génère un token JWT"""
    # form_data contient .username et .password
    user = get_user_by_name(db, form_data.username)

    if not user:
        logger.error("Utilisateur non trouvé")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )

    hashed_input_pwd = hash_password(form_data.password)

    if hashed_input_pwd != user.pswd:
        logger.error("Mot de passe incorrect")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"nom": user.nom, "email": user.email}
    )
    return JSONResponse({"access_token": access_token, "token_type": "bearer"})


@router_users.get("/me")
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Récupère les informations de l'utilisateur courant.
    """
    payload = decode_token(token)
    user = get_user_by_name(db, payload["nom"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )

    return {"nom": user.nom, "email": user.email}


@router_users.get("/is_connected")
async def get_connection_status(token: str = Depends(oauth2_scheme)):
    try:
        decode_token(token)
        return True
    except Exception:
        return False
