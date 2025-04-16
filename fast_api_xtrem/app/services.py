# app/services.py
from typing import Optional

from fast_api_xtrem.app.config import AppConfig
from fast_api_xtrem.db.db_manager import DBManager
from fast_api_xtrem.logger.logger_manager import LoggerManager


class ApplicationServices:
    """
    Classe contenant tous les services de l'application.
    Fournit un accès centralisé aux différents services
    et gère leur cycle de vie.
    """

    def __init__(self, config: AppConfig):
        """
        Initialise les services de l'application

        Args:
            config: Configuration de l'application
        """
        self.config = config
        self.logger: Optional[LoggerManager] = None
        self.db_manager: Optional[DBManager] = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialise et démarre tous les services"""
        if self._initialized:
            self.logger.warning("Services déjà initialisés")
            return

        # Initialisation du logger en premier
        # pour que les autres services puissent l'utiliser
        self.logger = LoggerManager()

        # Initialisation de la base de données
        self.db_manager = DBManager(
            database_url=self.config.database_url,
            logger=self.logger
        )

        self.db_manager.connect()
        self.db_manager.check_tables()

        self._initialized = True
        self.logger.info("Tous les services ont été initialisés")

    def cleanup(self) -> None:
        """Nettoie et ferme tous les services"""
        if not self._initialized:
            return

        if self.db_manager:
            self.db_manager.disconnect()

        if self.logger:
            self.logger.info("Tous les services ont été arrêtés")

        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        """
        Vérifie si les services sont initialisés

        Returns:
            bool: True si les services sont initialisés, False sinon
        """
        return self._initialized
