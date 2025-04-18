"""
Point d'entrée principal de l'application FastAPI Xtrem.

Ce fichier contient la fonction factory pour créer l'application,
ainsi que le point d'entrée pour exécuter l'application.

Il initialise les configurations nécessaires
et lance l'application via Uvicorn.
"""

import os
import sys

from prometheus_fastapi_instrumentator import Instrumentator

from fast_api_xtrem.app.application import Application
from fast_api_xtrem.app.config import AppConfig

# Add the project root to the Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def create_app() -> Application:
    """
    Fonction factory pour créer l'application.

    Returns:
        Application: Instance de l'application.
    """
    config = AppConfig()

    return Application(config)


# Point d'entrée principal
if __name__ == "__main__":
    app = create_app()
    Instrumentator().instrument(app.fast_api).expose(app.fast_api)
    app.run()
