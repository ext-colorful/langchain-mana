"""Sync service for ingredients and meals."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from app.core.logging import logger


@dataclass
class SyncState:
    name: str
    total: int = 0
    synced: int = 0
    is_syncing: bool = False
    task: asyncio.Task | None = None

    @property
    def remaining(self) -> int:
        return max(self.total - self.synced, 0)

    @property
    def progress_percentage(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.synced / self.total * 100, 2)


class SyncService:
    """Handles background sync tasks."""

    def __init__(self):
        self.ingredient_state = SyncState(name="ingredients")
        self.meal_state = SyncState(name="meals")

    async def start_ingredient_sync(self) -> str:
        return await self._start_sync(self.ingredient_state)

    async def start_meal_sync(self) -> str:
        return await self._start_sync(self.meal_state)

    async def _start_sync(self, state: SyncState) -> str:
        if state.is_syncing:
            return f"{state.name} sync already in progress"

        state.total = 10000 if state.name == "ingredients" else 5000
        state.synced = 0
        state.is_syncing = True
        state.task = asyncio.create_task(self._simulate_sync(state))
        logger.info(f"Started {state.name} sync task")
        return f"{state.name} sync started"

    async def _simulate_sync(self, state: SyncState):
        try:
            while state.synced < state.total:
                await asyncio.sleep(0.1)
                state.synced = min(state.synced + 500, state.total)
            logger.info(f"{state.name} sync completed")
        except Exception as exc:
            logger.error(f"Sync error: {exc}")
        finally:
            state.is_syncing = False

    def get_ingredient_status(self) -> dict:
        return self._status(self.ingredient_state)

    def get_meal_status(self) -> dict:
        return self._status(self.meal_state)

    def _status(self, state: SyncState) -> dict:
        return {
            "total": state.total,
            "synced": state.synced,
            "remaining": state.remaining,
            "progress_percentage": state.progress_percentage,
            "is_syncing": state.is_syncing,
        }
