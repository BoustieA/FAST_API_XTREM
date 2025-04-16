"""
Module de gestion des logs pour l'application Fast API Xtrem.

Ce module fournit une implémentation de gestionnaire de logs utilisant loguru
avec un pattern singleton pour assurer une instance unique dans l'application.
Il offre des fonctionnalités pour enregistrer des messages d'information,
d'erreur et de succès, ainsi qu'un décorateur pour capturer les exceptions.
"""

import os
import sys
from pathlib import Path

from loguru import logger


class LoggerManager:
    """
    Gestionnaire de logs utilisant loguru avec pattern singleton.
    """

    _instance = None
    _logs_dir = None

    def __new__(cls) -> "LoggerManager":
        if cls._instance is None:
            instance = super(LoggerManager, cls).__new__(cls)
            cls._instance = instance
            instance._initialize()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance for testing purposes."""
        cls._instance = None

    def _initialize(self) -> None:
        """
        Initialise le gestionnaire de logs avec le chemin des logs
        et configure loguru.
        """
        try:
            # Détermine le chemin du répertoire de logs relatif au module
            module_path = Path(os.path.dirname(os.path.abspath(__file__)))
            project_root = module_path.parent.parent
            self._logs_dir = project_root / "logs"

            # Création du répertoire de logs s'il n'existe pas
            if not self._logs_dir.exists():
                self._logs_dir.mkdir(parents=True)
                logger.info(f"Log directory created at: {self._logs_dir}")

            # Configuration de loguru
            log_file_path = self._logs_dir / "app.log"

            # Remove default handler and add our custom handlers
            logger.remove()

            # Add a handler for stdout (console)
            log_level = os.getenv("LOG_LEVEL", "INFO")
            logger.add(sys.stderr, level=log_level)

            # Add a handler for the log file
            logger.add(
                str(log_file_path),
                rotation="10 MB",
                retention="1 week",
                compression="zip",
                level=log_level,
                encoding="utf-8",
            )

            logger.info("Logger configured successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize LoggerManager: {e}")
            raise

    @property
    def logs_dir(self) -> Path:
        """Retourne le chemin du répertoire de logs."""
        return self._logs_dir

    @staticmethod
    def info(message: str) -> None:
        """Enregistre un message d'information."""
        logger.info(message)

    @staticmethod
    def error(message: str) -> None:
        """Enregistre un message d'erreur."""
        logger.error(message)

    @staticmethod
    def success(message: str) -> None:
        """Enregistre un message de succès."""
        logger.success(message)

    @staticmethod
    def debug(message: str) -> None:
        """Enregistre un message de débogage."""
        logger.debug(message)

    @staticmethod
    def warning(message: str) -> None:
        """Enregistre un message d'avertissement."""
        logger.warning(message)

    @staticmethod
    def catch(*args, **kwargs) -> callable:
        """
        Décorateur pour attraper et logger les exceptions.

        Returns:
            callable: Le décorateur catch de loguru
        """
        return logger.catch(*args, **kwargs)

    def __repr__(self) -> str:
        """
        Représentation textuelle de l'instance.

        Returns:
            str: Représentation de l'instance
        """
        return f"<LoggerManager logs_dir={self._logs_dir}>"
