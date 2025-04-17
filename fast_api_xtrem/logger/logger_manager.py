"""
Module de gestion des logs pour l'application FastAPI XTREM.

Ce module fournit une implémentation de gestionnaire de logs utilisant Loguru
avec un pattern singleton. Il offre des méthodes statiques pour enregistrer
différents niveaux de logs ainsi qu'un décorateur pour capturer les exceptions.
"""

import sys
from pathlib import Path

from loguru import logger

from fast_api_xtrem.app.config import LoggerConfig


class LoggerManager:
    """
    Gestionnaire de logs utilisant loguru (pattern singleton).

    Permet l'enregistrement des messages de logs vers la console et un fichier,
    avec rotation, compression, et gestion centralisée via AppConfig.
    """

    _instance = None
    _logs_dir: Path = None

    def __new__(cls, config: LoggerConfig) -> "LoggerManager":
        """Implémente le pattern singleton."""
        if cls._instance is None:
            instance = super(LoggerManager, cls).__new__(cls)
            cls._instance = instance
            instance._initialize(config)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """
        Réinitialise l'instance singleton.

        Utile pour les tests ou la réinitialisation manuelle.
        """
        cls._instance = None

    def _initialize(self, config: LoggerConfig) -> None:
        """
        Initialise le logger avec la configuration fournie.

        Args:
            config (AppConfig): Configuration contenant
            les paramètres du logger.
        """
        try:
            # Répertoire des logs : fast_api_xtrem/logs
            base_path = Path(__file__).resolve().parent.parent
            self._logs_dir = base_path / "logs"
            self._logs_dir.mkdir(parents=True, exist_ok=True)

            log_path = self._logs_dir / config.log_file_name

            # Suppression des handlers précédents
            logger.remove()

            # Log vers la console (coloré)
            logger.add(sys.stderr, level=config.log_level)

            # Log vers le fichier (non coloré)
            logger.add(
                str(log_path),
                rotation=config.log_rotation,
                retention=config.log_retention,
                compression=config.log_compression,
                level=config.log_level,
                encoding=config.log_encoding,
                colorize=False,
            )

            logger.info("Logger initialized with config from AppConfig.")
        except Exception as e:
            logger.error(f"Logger initialization failed: {e}")
            raise

    @property
    def logs_dir(self) -> Path:
        """
        Retourne le chemin du répertoire des logs.

        Returns:
            Path : Répertoire où sont stockés les fichiers de log.
        """
        return self._logs_dir

    @staticmethod
    def info(message: str) -> None:
        """Log un message d'information."""
        logger.info(message)

    @staticmethod
    def error(message: str) -> None:
        """Log un message d'erreur."""
        logger.error(message)

    @staticmethod
    def success(message: str) -> None:
        """Log un message de succès."""
        logger.success(message)

    @staticmethod
    def debug(message: str) -> None:
        """Log un message de debug."""
        logger.debug(message)

    @staticmethod
    def warning(message: str) -> None:
        """Log un message d'avertissement."""
        logger.warning(message)

    @staticmethod
    def catch(*args, **kwargs) -> callable:
        """
        Retourne un décorateur pour capturer les exceptions avec Loguru.

        Returns:
            callable: Décorateur de fonction.
        """
        return logger.catch(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<LoggerManager logs_dir={self._logs_dir}>"
