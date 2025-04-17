"""
Module de configuration statique de l'application FastAPI XTREM.

Ce module définit la classe `AppConfig`, qui regroupe toutes les options
de configuration de l'application : FastAPI, base de données et logs.
"""

from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    """Configuration de la base de données pour l'application."""

    database_url: str = "sqlite:///./fast_api_xtrem/db/app_data.db"


@dataclass
class NetworkConfig:
    """Configuration réseau pour l'application (hôte et port)."""

    host: str = "127.0.0.1"
    port: int = 8000


@dataclass
class LoggerConfig:
    """Configuration des logs pour l'application
    (niveau, fichier, rotation)."""

    log_level: str = "INFO"
    log_file_name: str = "app.log"
    log_rotation: str = "10 MB"
    log_retention: str = "1 week"
    log_compression: str = "zip"
    log_encoding: str = "utf-8"


@dataclass
class AppConfig:
    """Configuration générale de l'application FastAPI XTREM."""

    title: str = "Hello World API"
    description: str = "API démonstration FastAPI avec gestion de BDD SQLite"
    version: str = "1.0.0"
    reload: bool = False
    database_config: DatabaseConfig = field(default_factory=DatabaseConfig)
    network_config: NetworkConfig = field(default_factory=NetworkConfig)
    logger_config: LoggerConfig = field(default_factory=LoggerConfig)

    def __post_init__(self) -> None:
        """Validation simple de la configuration."""
        if not self.database_config.database_url:
            raise ValueError("L'URL de la base de données est requise.")
        if not self.title:
            raise ValueError("Le titre de l'application est requis.")
        if not isinstance(self.network_config.port, int):
            raise ValueError("Le port doit être un entier.")
