"""
Health check routes for the FastAPI application.

This module contains endpoints related to service health monitoring
and status reporting.
"""

from fastapi import APIRouter

router_health = APIRouter()


@router_health.get("/health")
async def health() -> dict:
    """
    Health check endpoint

    Returns:
        dict: Simple status response indicating API health
    """
    return {"status": "ok"}
