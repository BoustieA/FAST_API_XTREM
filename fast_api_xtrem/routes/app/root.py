# routes/root.py
from fastapi import (
    APIRouter,
    Depends,
    Request
)

router_root = APIRouter()


def get_logger(request: Request):
    return request.app.state.logger


@router_root.get("/", tags=["Root"])
async def root(logger=Depends(get_logger)):
    logger.info("Appel de la route root")
    return {
        "message": "Hello World",
        "docs": "/docs",
        "redoc": "/redoc"
    }
