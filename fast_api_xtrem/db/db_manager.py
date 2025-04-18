"""
Module de gestion de la base de données pour l'application FastAPI Xtrem.

Ce module contient la classe DBManager, responsable de la connexion à la base
de données, de la création des tables, de la gestion des sessions SQLAlchemy
et de la vérification des structures existantes.

Il définit également une exception personnalisée pour les erreurs de connexion.
"""

from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from fast_api_xtrem.app.config import DatabaseConfig, LoggerConfig
from fast_api_xtrem.db.base import Base
from fast_api_xtrem.db.utils.utils import seed_default_roles
from fast_api_xtrem.logger.logger_manager import LoggerManager


class DBConnectionError(RuntimeError):
    """
    Exception personnalisée pour les erreurs de connexion
    à la base de données.
    """


class DBManager:
    """
    Classe responsable de la gestion de la base de données.

    Elle gère l'initialisation du moteur SQLAlchemy, la création des tables,
    la gestion des sessions, et fournit des utilitaires
    comme la vérification des tables.
    """

    def __init__(
        self, config: DatabaseConfig, logger_config: LoggerConfig, logger=None
    ):
        """
        Initialise le gestionnaire de base de données.

        Args:
            config (AppConfig) : Configuration de l'application contenant
                                l'URL de la base de données.
            logger: Instance du gestionnaire de logs.
        """
        self.config = config
        self.database_url = config.database_url
        self.engine = None
        self.session_local = None
        self.logger = logger or LoggerManager(logger_config)
        self._check_db_file()

    @staticmethod
    def _get_package_root() -> Path:
        """Retourne le chemin racine du package fast_api_xtrem."""
        current_file = Path(__file__)
        package_root = current_file.parent.parent
        return package_root

    def _check_db_file(self):
        """
        Vérifie si le fichier de base de données existe,
        l'extrait de l'URL SQLite, et crée le dossier si besoin.
        """
        if self.database_url.startswith("sqlite:///"):
            package_root = self._get_package_root()
            database_dir = package_root / "database"
            if not database_dir.exists():
                database_dir.mkdir(exist_ok=True)
                self.logger.info(
                    f"Création du répertoire pour la base de données: "
                    f"{database_dir}"
                )

            db_file = database_dir / "app_data.db"
            self.database_url = f"sqlite:///{db_file.absolute()}"

            if db_file.exists():
                self.logger.info(
                    f"Utilisation de la base de données existante: {db_file}"
                )
            else:
                self.logger.info(
                    f"Le fichier de base de données sera créé: {db_file}"
                )

    def _create_tables(self):
        """Crée les tables dans la base de données si elles n'existent pas."""
        self.logger.info("Création des tables")
        for table_name in Base.metadata.tables.keys():
            self.logger.info(f"Création de la table: {table_name}")
        Base.metadata.create_all(bind=self.engine)
        self.logger.success("✅ Tables crées")
        # Alimentation des rôles par défaut [[4]]
        seed_default_roles(self.engine, self.logger)

    def connect(self):
        """Connexion avec vérifications supplémentaires."""
        if self.engine:
            self.logger.warning("Connexion déjà établie")
            return False  # Évite les connexions multiples [[9]]

        try:
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                pool_pre_ping=True,  # Vérifie la validité des connexions [[5]]
            )
            self._create_tables()
            self.session_local = sessionmaker(bind=self.engine)
            self.logger.success("✅ Connexion réussie")
            return True
        except Exception as e:
            self.logger.error(f"Échec de connexion : {str(e)}")
            raise DBConnectionError from e

    def disconnect(self):
        """Ferme proprement la connexion à la base de données."""
        if self.engine:
            self.engine.dispose()
            self.logger.info("🔌 Déconnexion de la base de données effectuée")
        else:
            self.logger.warning(
                "Tentative de déconnexion sans connexion active"
            )

    def get_db(self):
        """Fournit une session SQLAlchemy."""
        if not self.session_local:
            self.logger.error("Session non initialisée")
            raise DBConnectionError("Base de données non connectée")

        db = self.session_local()
        try:
            yield db
        except Exception as e:
            db.rollback()
            self.logger.error(f"Erreur de session : {str(e)}")
            raise
        finally:
            db.close()  # Fermeture explicite [[6]]

    def check_tables(self):
        """
        Vérifie les tables existantes dans la base de données.

        Returns:
            list[str] : Noms des tables détectées.
        """
        if not self.engine:
            self.logger.error(
                "Impossible de vérifier les tables sans connexion active"
            )
            return []

        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        if tables:
            self.logger.info(f"Tables existantes: {', '.join(tables)}")
        else:
            self.logger.info(
                "Aucune table n'existe encore dans la base de données"
            )
        return tables
