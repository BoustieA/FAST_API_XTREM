import contextlib

from fastapi import FastAPI
from loguru import logger

from db.db_manager import DBManager

# Initialisation du gestionnaire de base de données
db_manager = DBManager()

@contextlib.asynccontextmanager
async def lifespan():
    logger.info("Démarrage de l'application")
    db_manager.connect()
    yield
    logger.info("Arrêt de l'application")
    db_manager.disconnect()

# Initialisation de l'application
app = FastAPI(
    lifespan=lifespan,
    title="Hello World API",
    description="API démonstration FastAPI",
    version="1.0.0"
)

@app.get("/favicon.ico", status_code=204)
async def favicon() -> None:
    """
    Endpoint renvoyant un code d'état 204 pour le favicon.
    Ce endpoint est utilisée par les navigateurs web pour récupérer le favicon.
    """
    return

@app.get("/", tags=["Root"])
async def root():
    """Endpoint racine retournant un message de bienvenue"""
    return {
        "message": "Hello World",
        "docs": "http://localhost:8000/docs",
        "redoc": "http://localhost:8000/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)