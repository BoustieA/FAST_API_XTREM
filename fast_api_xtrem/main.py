# main.py
import os
import sys
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI

from fast_api_xtrem.app.config import AppConfig
from fast_api_xtrem.app.services import ApplicationServices
from fast_api_xtrem.app.state import AppState
from fast_api_xtrem.routes.app.favicon import router_favicon
from fast_api_xtrem.routes.app.root import router_root
from fast_api_xtrem.routes.db.users import router_users

# Add the project root to the Python path
# This is crucial for resolving imports correctly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


class Application:
    """Classe représentant l'application FastAPI avec ses services"""

    def __init__(self, config: AppConfig):
        """
        Initialise l'application avec sa configuration

        Args:
            config: Configuration de l'application
        """
        self.config = config
        self.services: Optional[ApplicationServices] = None
        self.app_state = AppState()
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        """
        Crée et configure l'instance FastAPI

        Returns:
            FastAPI: Instance configurée de FastAPI
        """
        fastapi_app = FastAPI(
            title=self.config.title,
            description=self.config.description,
            version=self.config.version,
            lifespan=self._lifespan
        )

        # Inclusion des routes
        fastapi_app.include_router(router_root)
        fastapi_app.include_router(router_favicon)
        fastapi_app.include_router(router_users)

        return fastapi_app

    @asynccontextmanager
    async def _lifespan(self, fastapi_app: FastAPI):
        """
        Gestion du cycle de vie de l'application
        avec initialisation/fermeture des services

        """
        # Initialisation des services
        self.services = ApplicationServices(self.config)
        self.services.initialize()

        # Mise à disposition des services dans l'état de l'application
        # Utilisation de notre gestionnaire d'état personnalisé
        self.app_state.set("services", self.services)

        # On attache notre gestionnaire d'état à l'application
        setattr(fastapi_app, "app_state", self.app_state)
        # Expose logger on FastAPI state for dependencies
        fastapi_app.state.logger = self.services.logger

        yield

        # Nettoyage des ressources
        if self.services:
            self.services.cleanup()

    def run(self):
        """Lance l'application avec uvicorn"""

        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            reload=True
        )


def create_app() -> Application:
    """
    Fonction factory pour créer l'application

    Returns:
        Application: Instance de l'application
    """
    config = AppConfig(
        title="Hello World API",
        description="API démonstration FastAPI avec gestion de BDD SQLite",
        version="1.0.0",
        database_url="sqlite:///./fast_api_xtrem/db/app_data.db",
        host="127.0.0.1",
        port=8000
    )

    return Application(config)


# Point d'entrée principal
if __name__ == "__main__":
    app = create_app()
    app.run()
