"""Session repository interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from app.domain.entities.session import Session


class SessionRepository(ABC):
    """Interface for session persistence."""

    @abstractmethod
    async def create_session(self, session: Session) -> Session:
        raise NotImplementedError

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[Session]:
        raise NotImplementedError

    @abstractmethod
    async def update_session(self, session: Session) -> Session:
        raise NotImplementedError

    @abstractmethod
    async def add_message(self, session_id: str, message: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_sessions(self, user_id: str) -> Iterable[Session]:
        raise NotImplementedError
