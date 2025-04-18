"""
Modèle de la table 'users' pour la base de données.

Ce module définit la structure de la table utilisateur,
incluant l'identifiant, le nom, l'email et le mot de passe.
"""

from sqlalchemy import Column, Integer, String

from fast_api_xtrem.db.base import Base


# pylint: disable=too-few-public-methods
class User(Base):
    """
    Représente un utilisateur dans la base de données.

    Attributs :
        id (int) : Identifiant unique de l'utilisateur.
        nom (str) : Nom complet de l'utilisateur.
        email (str) : Adresse email de l'utilisateur.
        pswd (str) : Mot de passe de l'utilisateur (non chiffré ici).
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    pswd = Column(String(100), nullable=False)
