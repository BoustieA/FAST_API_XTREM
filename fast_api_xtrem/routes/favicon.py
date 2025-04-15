# routes/favicon.py
from fastapi import APIRouter, Depends, Request

router_favicon = APIRouter()


def get_logger(request: Request):
    return request.app.state.logger


@router_favicon.get("/favicon.ico", status_code=204)
async def favicon(logger=Depends(get_logger)):
    logger.info("Appel de la favicon")
    return None
