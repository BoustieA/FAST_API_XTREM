# app/config.py

"""
Module de configuration de l'application FastAPI XTREM.

Ce module définit la classe AppConfig qui est utilisée pour
gérer la configuration de l'application, y compris les
paramètres de la base de données, le titre, la description
et d'autres options de configuration nécessaires au bon
fonctionnement de l'application.
"""

from dataclasses import dataclass

@dataclass
class AppConfig:
    """Configuration de l'application.

    Attributes :
        title (str) : Titre de l'application.
        description (str) : Description de l'application.
        version (str) : Version de l'application.
        database_url (str) : URL de connexion à la base de données.
        host (str) : Adresse IP d'écoute (par défaut : "127.0.0.1").
        port (int) : Port d'écoute (par défaut : 8000).
    """

    title: str
    description: str
    version: str
    database_url: str
    host: str = "127.0.0.1"
    port: int = 8000

    def __post_init__(self) -> None:
        """Validation de la configuration après initialisation.

        Raises :
            ValueError : Si l'URL de la base de données ou le titre de l'application est manquant.
        """
        if not self.database_url:
            raise ValueError("L'URL de la base de données est requise")
        if not self.title:
            raise ValueError("Le titre de l'application est requis")
