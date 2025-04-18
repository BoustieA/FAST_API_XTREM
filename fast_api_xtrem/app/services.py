"""
Module contenant la classe ApplicationServices qui gère le cycle de vie des
services de l'application FastAPI XTREM.

La classe `ApplicationServices` centralise l'accès aux différents services
de l'application, comme le gestionnaire de base de données
et le gestionnaire de logs.
Elle fournit des méthodes pour initialiser et nettoyer ces services de
manière centralisée.

Elle est utilisée pour connecter la base de données, gérer l'état des services,
et assurer un démarrage et un arrêt propres de l'application.
"""

from fast_api_xtrem.app.config import AppConfig
from fast_api_xtrem.db.db_manager import DBManager
from fast_api_xtrem.logger.logger_manager import LoggerManager


class ApplicationServices:
    """
    Classe contenant tous les services de l'application FastAPI XTREM.
    Fournit un accès centralisé aux différents services
    et gère leur cycle de vie.
    """

    def __init__(self, config: AppConfig) -> None:
        """
        Initialise les services de l'application.

        Args:
            config: Configuration de l'application.
        """
        self.config = config
        # Instancier le logger en amont pour l'ensemble des services
        self.logger = LoggerManager(self.config.logger_config)
        # Créer l'instance de DBManager en passant le logger
        self.db_manager = DBManager(
            config=self.config.database_config,
            logger_config=self.config.logger_config,
            logger=self.logger,
        )
        self._initialized = False

    def initialize(self) -> None:
        """
        Initialise et démarre tous les services.
        Ne fait l'initialisation qu'une seule fois.

        Cette méthode établit la connexion à la base de données,
        crée les tables nécessaires si elles n'existent pas,
        et effectue toute autre initialisation requise pour
        le bon fonctionnement des services.

        Si les services ont déjà été initialisés,
        un avertissement est enregistré.
        """
        if self._initialized:
            self.logger.warning("Services déjà initialisés")
            return

        # Connexion à la base de données et création des tables
        try:
            self.db_manager.connect()
        except Exception as e:
            self.logger.error(
                f"Échec de la connexion à la base de données : {e}"
            )
            raise

        # Optionnel : afficher les tables existantes pour debug
        tables = self.db_manager.check_tables()
        self.logger.info(f"Tables dans la BD au démarrage : {tables}")

        self._initialized = True
        self.logger.info("✅ Tous les services ont été initialisés")

    def cleanup(self) -> None:
        """
        Nettoie et ferme tous les services.

        Cette méthode effectue la déconnexion de la base de données et arrête
        proprement tous les services initialisés.
        Elle doit être appelée lorsque l'application est arrêtée
        ou lors de la fermeture des services.

        Si les services n'ont pas été initialisés, rien ne se passe.
        """
        if not self._initialized:
            return

        # Déconnexion propre de la base
        self.db_manager.disconnect()
        self.logger.info("🔌 Déconnexion de la base de données effectuée")

        self.logger.info("🛑 Tous les services ont été arrêtés")
        self._initialized = False
