"""
Route racine de l'application FastAPI.

Fournit un point d'entrée basique pour tester que l'API fonctionne
et redirige vers la documentation.
"""

from fastapi import APIRouter, Depends, Request

router_root = APIRouter()


def get_logger(request: Request):
    """
    Récupère le logger depuis l'état de l'application.

    Args:
        request (Request) : Requête HTTP entrante.

    Returns:
        Logger : L'instance du logger.
    """
    return request.app.state.logger


@router_root.get("/", tags=["Root"])
async def root(logger=Depends(get_logger)):
    """
    Route GET pour la racine de l'API.

    Args:
        logger: Logger injecté via Depends.

    Returns:
        dict: Message de bienvenue et liens vers la documentation.
    """
    logger.info("Appel de la route root")
    return {
        "message": "Hello World",
        "docs": "/docs",
        "redoc": "/redoc",
        "metrics": "/metrics"
    }
