"""
Route pour la gestion du favicon.

Ce module intercepte les requêtes vers /favicon.ico afin d'éviter
des erreurs 404 dans les navigateurs web, en renvoyant un code 204.
"""

from fastapi import APIRouter, Depends, Request

router_favicon = APIRouter()


def get_logger(request: Request):
    """
    Récupère l'instance du logger depuis l'état de l'application.

    Args:
        request (Request): La requête HTTP FastAPI.

    Returns:
        Logger: L'instance du logger.
    """
    return request.app.state.logger


@router_favicon.get("/favicon.ico", status_code=204)
async def favicon(logger=Depends(get_logger)):
    """
    Route pour intercepter /favicon.ico et éviter une erreur 404.

    Args:
        logger: Le logger injecté via Depends.

    Returns:
        None: Réponse vide avec le code 204 (No Content).
    """
    logger.info("Appel de la favicon")
    return None
