import pathlib

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from fast_api_xtrem.db.base import Base
from fast_api_xtrem.logger.logger_manager import LoggerManager


class DBManager:
    def __init__(self, database_url: str, logger=None):
        """
        Initialise le gestionnaire de base de données.

        Args:
            database_url: URL de connexion à la base de données SQLite
            logger: Instance du gestionnaire de logs
        """
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self.logger = logger or LoggerManager()
        self._check_db_file()

    @staticmethod
    def _get_package_root():
        """Retourne le chemin racine du package fast_api_xtrem"""
        # Obtenir le chemin du module courant
        current_file = pathlib.Path(__file__)
        # Remonter jusqu'à la racine du package fast_api_xtrem
        package_root = current_file.parent.parent
        return package_root

    def _check_db_file(self):
        """Vérifie si le fichier de base de données existe,
        l'extrait de l'URL SQLite"""
        if self.database_url.startswith("sqlite:///"):
            # Obtenir la racine du package
            package_root = self._get_package_root()

            # Créer le répertoire database à la racine du package
            database_dir = package_root / "database"
            if not database_dir.exists():
                database_dir.mkdir(exist_ok=True)
                self.logger.info(
                    f"Création du répertoire pour la base de données: "
                    f"{database_dir}")

            # Définir le chemin complet du fichier de base de données
            db_file = database_dir / "app_data.db"

            # Mettre à jour l'URL de la base de données avec le chemin absolu
            self.database_url = f"sqlite:///{db_file.absolute()}"

            db_exists = db_file.exists()
            if db_exists:
                self.logger.info(
                    f"Utilisation de la base de données existante: "
                    f"{db_file}")
            else:
                self.logger.info(
                    f"Le fichier de base de données sera créé: {db_file}")

    def _create_tables(self):
        self.logger.info("Création des tables")
        from fast_api_xtrem.db.models.user import User
        # Référencer User pour éviter l'erreur d'importation non utilisée
        self.logger.info(f"Modèle chargé: {User.__name__}")
        for table_name in Base.metadata.tables.keys():
            self.logger.info(f"Création de la table: {table_name}")
        Base.metadata.create_all(bind=self.engine)

    def connect(self):
        """Établit la connexion à la base de données SQLite"""
        try:
            self.logger.info(f"Tentative de connexion à: {self.database_url}")
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False}
                # Nécessaire pour SQLite
            )

            # Création des tables si elles n'existent pas
            self._create_tables()

            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Vérification que la connexion fonctionne
            with self.engine.connect() as conn:
                with conn.begin():
                    pass

            self.logger.success(f"✅ Connecté à la base de données: "
                                f"{self.database_url}")
            return True

        except Exception as e:
            self.logger.error(
                f"❌ Erreur de connexion à la base de données: {str(e)}")
            raise

    def disconnect(self):
        """Ferme proprement la connexion à la base de données"""
        if self.engine:
            self.engine.dispose()
            self.logger.info("🔌 Déconnexion de la base de données effectuée")
        else:
            self.logger.warning(
                "Tentative de déconnexion sans connexion active")

    def get_db(self):
        """Fournit une session de base de données
        pour les dépendances FastAPI"""
        if not self.SessionLocal:
            self.logger.error(
                "Tentative d'obtenir une session sans connexion active")
            raise Exception("Base de données non connectée")

        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def check_tables(self):
        """Vérifie les tables existantes dans la base de données"""
        if not self.engine:
            self.logger.error(
                "Impossible de vérifier les tables sans connexion active")
            return []

        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        if tables:
            self.logger.info(f"Tables existantes: {', '.join(tables)}")
        else:
            self.logger.info(
                "Aucune table n'existe encore dans la base de données")
        return tables
