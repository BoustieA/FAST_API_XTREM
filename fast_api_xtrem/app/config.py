# app/config.py
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Configuration de l'application"""

    title: str
    description: str
    version: str

    database_url: str
    host: str = "127.0.0.1"
    port: int = 8000

    def __post_init__(self):
        """Validation de la configuration après initialisation"""

        if not self.database_url:
            raise ValueError("L'URL de la base de données est requise")
        if not self.title:
            raise ValueError("Le titre de l'application est requis")