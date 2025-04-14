import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from logger.logger_manager import LoggerManager

Base = declarative_base()


class DBManager:
    def __init__(self, database_url: str = "sqlite:///./database.db", logger=None):
        """
        Initialise le gestionnaire de base de données

        Args:
            database_url: URL de connexion à la base de données SQLite
            logger: Instance du gestionnaire de logs
        """
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self.logger = logger or LoggerManager()
        self._check_db_file()

    def _check_db_file(self):
        """Vérifie si le fichier de base de données existe, l'extrait de l'URL SQLite"""
        if self.database_url.startswith("sqlite:///"):
            # Extraire le chemin du fichier de la chaîne de connexion SQLite
            db_file = self.database_url.replace("sqlite:///", "")

            # Assurez-vous que le répertoire parent existe
            db_dir = os.path.dirname(db_file)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                self.logger.info(f"Création du répertoire pour la base de données: {db_dir}")

            db_exists = os.path.exists(db_file)

            if db_exists:
                self.logger.info(f"Utilisation de la base de données existante: {db_file}")
            else:
                self.logger.info(f"Le fichier de base de données sera créé: {db_file}")

    def connect(self):
        """Établit la connexion à la base de données SQLite"""
        try:
            self.logger.info(f"Tentative de connexion à: {self.database_url}")
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False}  # Nécessaire pour SQLite
            )

            # Création des tables si elles n'existent pas
            Base.metadata.create_all(bind=self.engine)

            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Vérification que la connexion fonctionne
            with self.engine.connect() as conn:
                with conn.begin():
                    pass

            self.logger.success(f"✅ Connecté à la base de données: {self.database_url}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erreur de connexion à la base de données: {str(e)}")
            raise

    def disconnect(self):
        """Ferme proprement la connexion à la base de données"""
        if self.engine:
            self.engine.dispose()
            self.logger.info("🔌 Déconnexion de la base de données effectuée")
        else:
            self.logger.warning("Tentative de déconnexion sans connexion active")

    def get_db(self):
        """Fournit une session de base de données pour les dépendances FastAPI"""
        if not self.SessionLocal:
            self.logger.error("Tentative d'obtenir une session sans connexion active")
            raise Exception("Base de données non connectée")

        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def check_tables(self):
        """Vérifie les tables existantes dans la base de données"""
        if not self.engine:
            self.logger.error("Impossible de vérifier les tables sans connexion active")
            return []

        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        if tables:
            self.logger.info(f"Tables existantes: {', '.join(tables)}")
        else:
            self.logger.info("Aucune table n'existe encore dans la base de données")
        return tables

# Suppression de la fonction lifespan qui n'est plus nécessaire ici