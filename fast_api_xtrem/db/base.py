"""
Module de définition de la base de données SQLAlchemy
pour l'application FastAPI XTREM.

Ce module crée une instance unique de la classe `Base`, utilisée comme base
pour tous les modèles SQLAlchemy de l'application. Il expose également une
fonction utilitaire `get_base` pour accéder à cette base
depuis d'autres modules.
"""

from sqlalchemy.ext.declarative import declarative_base

# Créer la base une seule fois, ici
Base = declarative_base()


def get_base():
    """
    Retourne l'instance unique de la base déclarative SQLAlchemy.

    Returns:
        Base: Classe de base pour les modèles SQLAlchemy.
    """
    return Base
