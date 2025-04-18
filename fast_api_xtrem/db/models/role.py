"""
Définit le modèle Role utilisé pour représenter les rôles d'utilisateurs
dans la base de données.

Chaque rôle possède un identifiant unique et un libellé
"""

from sqlalchemy import Column, Integer, String

from fast_api_xtrem.db.base import Base


# pylint: disable=too-few-public-methods
class Role(Base):
    """
    Représente un rôle d'utilisateur dans la base de données.

    Attributs :
        id (int) : Identifiant unique du rôle.
        libelle (str) : Nom ou libellé du rôle (ex. : "admin", "utilisateur").
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    libelle = Column(String(50), nullable=False)
