"""Tools API endpoints
"""
from typing import List

from fastapi import APIRouter, Depends

from ...core.security import get_current_user
from ...tools.base import ToolMetadata, tool_registry
from ...utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/list", response_model=List[ToolMetadata])
async def list_tools(
    category: str = None,
    current_user: dict = Depends(get_current_user)
):
    """List all available tools"""
    try:
        tools = tool_registry.list_tools(category=category)
        return tools
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        return []


@router.get("/{tool_name}", response_model=ToolMetadata)
async def get_tool(
    tool_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get tool details"""
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool.metadata
