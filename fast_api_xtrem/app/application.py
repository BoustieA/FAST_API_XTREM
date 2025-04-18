"""Module principal de l'application FastAPI."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI

from fast_api_xtrem.app.config import AppConfig
from fast_api_xtrem.app.services import ApplicationServices
from fast_api_xtrem.routes.app.favicon import router_favicon
from fast_api_xtrem.routes.app.root import router_root
from fast_api_xtrem.routes.db.users import router_users


# pylint: disable=too-few-public-methods
class Application:
    """Classe représentant l'application FastAPI avec ses services."""

    def __init__(self, config: AppConfig) -> None:
        """
        Initialise l'application avec sa configuration.

        Args:
            config (AppConfig): Configuration de l'application.
        """
        self.config: AppConfig = config
        self.services: Optional[ApplicationServices] = None
        self.fast_api: FastAPI = self._create_fast_api()

    def _create_fast_api(self) -> FastAPI:
        """
        Crée et configure l'instance FastAPI.

        Returns:
            FastAPI: Instance configurée de FastAPI.
        """
        fastapi_app: FastAPI = FastAPI(
            title=self.config.title,
            description=self.config.description,
            version=self.config.version,
            lifespan=self._lifespan,
        )

        # Inclusion des routes
        fastapi_app.include_router(router_root)
        fastapi_app.include_router(router_favicon)
        fastapi_app.include_router(router_users)

        return fastapi_app

    @asynccontextmanager
    async def _lifespan(
        self, fastapi_app: FastAPI
    ) -> AsyncGenerator[None, None]:
        """Contexte de vie de l'application (démarrage/arrêt)."""
        self.services = ApplicationServices(self.config)
        self.services.initialize()
        fastapi_app.state.services = self.services
        fastapi_app.state.logger = self.services.logger
        yield
        self.services.cleanup()
