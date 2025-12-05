"""Models API endpoints
"""
from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from ...core.security import get_current_user
from ...models.router import model_router
from ...utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/list", response_model=Dict[str, List[str]])
async def list_models(current_user: dict = Depends(get_current_user)):
    """List all available models"""
    try:
        models = model_router.list_available_models()
        return models
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return {}


@router.get("/{provider}/{model_name}", response_model=Dict[str, Any])
async def get_model_info(
    provider: str,
    model_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a model"""
    try:
        info = model_router.get_model_info(provider, model_name)
        return info
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        return {"error": str(e)}
