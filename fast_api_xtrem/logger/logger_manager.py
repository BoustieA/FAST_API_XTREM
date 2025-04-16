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

    def __new__(cls) -> "LoggerManager":
        if cls._instance is None:
            instance = super(LoggerManager, cls).__new__(cls)
            # Set cls._instance before calling _initialize
            cls._instance = instance
            instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """
        Initialise le gestionnaire de logs avec le chemin des logs
        et configure loguru.
        """
        # Initialize logs_dir attribute first to avoid AttributeError
        self.logs_dir = None

        # Détermine le chemin du répertoire de logs relatif au module
        module_path = Path(os.path.dirname(os.path.abspath(__file__)))
        project_root = module_path.parent.parent
        self.logs_dir = project_root / "logs"

        # Création du répertoire de logs s'il n'existe pas
        if not self.logs_dir.exists():
            self.logs_dir.mkdir(parents=True)
            print(f"Log directory created at: {self.logs_dir}")

        # Configuration de loguru
        log_file_path = self.logs_dir / "app.log"

        # Remove default handler and add our custom handlers
        logger.remove()

        # Add a handler for stdout (console)
        logger.add(sys.stderr, level="INFO")

        # Add a handler for the log file
        logger.add(
            str(log_file_path),
            rotation="10 MB",
            retention="1 week",
            compression="zip",
            level="INFO",
            encoding="utf-8",
        )

        print("Logger configured successfully.")

    @staticmethod
    def info(message: str) -> None:
        """
        Enregistre un message d'information.

        Args:
            message: Le message à enregistrer
        """
        logger.info(message)

    @staticmethod
    def error(message: str) -> None:
        """
        Enregistre un message d'erreur.

        Args:
            message : Le message d'erreur à enregistrer
        """
        logger.error(message)

    @staticmethod
    def success(message: str) -> None:
        """
        Enregistre un message de succès.

        Args:
            message: Le message de succès à enregistrer
        """
        logger.success(message)

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
        return f"<LoggerManager logs_dir={self.logs_dir}>"
