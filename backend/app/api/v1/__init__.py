"""API v1 routes
"""
from fastapi import APIRouter

from . import agents, knowledge, models, tools

api_router = APIRouter()

api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
