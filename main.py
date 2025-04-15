from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.db_manager import DBManager
from logger.logger_manager import LoggerManager


def initialize_services():
    """Initialisation centrale des services"""
    # Initialisation et configuration du logger
    logger = LoggerManager()
    logger.info("Initialisation des services")

    # Connexion à la base de données
    db_manager = DBManager(database_url="sqlite:///./db/app_data.db", logger=logger)
    db_manager.connect()
    db_manager.check_tables()

    return db_manager, logger


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    db_manager, logger = initialize_services()

    logger.info("🚀 Démarrage de l'application")
    yield
    logger.info("🛑 Arrêt de l'application")
    db_manager.disconnect()


app = FastAPI(
    title="Hello World API",
    description="API démonstration FastAPI avec gestion de BDD SQLite",
    version="1.0.0",
    lifespan=lifespan
)

# Récupération du logger pour les décorateurs
# On évite de réexécuter initialize_services() pour ne pas avoir de doubles connexions
# On crée juste une instance de LoggerManager pour les décorateurs
logger_instance = LoggerManager()


@app.get("/favicon.ico", status_code=204)
@logger_instance.catch(FileNotFoundError)
async def favicon() -> None:
    return


@app.get("/", tags=["Root"])
@logger_instance.catch(Exception)
async def root():
    return {
        "message": "Hello World",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
