"""
Module de configuration de l'application FastAPI XTREM.

Ce module définit la classe `AppConfig`, qui est responsable de la gestion de
la configuration de l'application, y compris des paramètres comme le titre,
la description, la version, ainsi que l'URL de la base de données, l'adresse
IP d'écoute, et le port d'écoute.

Il utilise les variables d'environnement pour la configuration,
avec des valeurs
par défaut définies dans le code. La classe `AppConfig` inclut des validations
pour assurer la présence de certains paramètres essentiels.
"""

import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Configuration de l'application FastAPI XTREM."""

    title: str = "Hello World API"
    description: str = "API démonstration FastAPI avec gestion de BDD SQLite"
    version: str = "1.0.0"
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite:///./fast_api_xtrem/db/app_data.db"
    )
    host: str = os.getenv("APP_HOST", "127.0.0.1")
    port: int = int(
        os.getenv("APP_PORT", "8000")
    )  # Convertir en int explicitement

    def __init__(self):
        """Initialisation des attributs de la configuration."""
        self.reload = None

    def __post_init__(self) -> None:
        """Validation de la configuration après initialisation.

        Cette méthode vérifie que les paramètres essentiels
        de la configuration
        sont présents et valides. Si des paramètres sont manquants
        ou invalides, une exception `ValueError` est levée.

        Raises:
            ValueError: Si l'URL de la base de données
            ou le titre de l'application est manquant.
        """
        if not self.database_url:
            raise ValueError("L'URL de la base de données est requise")
        if not self.title:
            raise ValueError("Le titre de l'application est requis")
