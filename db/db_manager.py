from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DBManager:
    def __init__(self, database_url: str = "sqlite:///./database.db"):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None

    def connect(self):
        """Établit la connexion à la base de données"""
        try:
            self.engine = create_engine(
                self.database_url, 
                connect_args={"check_same_thread": False}
            )
            self.SessionLocal = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=self.engine
            )
            logger.success(f"Connecté à la base de données : {self.database_url}")
            
        except Exception as e:
            logger.error(f"Erreur de connexion : {str(e)}")
            raise

    def disconnect(self):
        """Ferme proprement la connexion à la base de données"""
        if self.engine:
            self.engine.dispose()
            logger.info("Déconnexion de la base de données effectuée")

    def get_db(self):
        """Fournit une session de base de données pour les dépendances FastAPI"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
