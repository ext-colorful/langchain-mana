"""Sync endpoints."""

from fastapi import APIRouter, Request

from app.application.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["sync"])


def get_sync_service(request: Request) -> SyncService:
    if not hasattr(request.app.state, "sync_service"):
        request.app.state.sync_service = SyncService()
    return request.app.state.sync_service


@router.post("/start-sync")
async def start_sync(request: Request):
    service = get_sync_service(request)
    message = await service.start_ingredient_sync()
    return {"message": message}


@router.get("/sync-progress")
async def sync_progress(request: Request):
    service = get_sync_service(request)
    return service.get_ingredient_status()


@router.post("/meal/start-sync")
async def start_meal_sync(request: Request):
    service = get_sync_service(request)
    message = await service.start_meal_sync()
    return {"message": message}


@router.get("/meal/sync-progress")
async def meal_sync_progress(request: Request):
    service = get_sync_service(request)
    return service.get_meal_status()
