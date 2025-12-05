"""Session and message management service."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.core.logging import logger
from app.domain.entities.session import Message, Session
from app.domain.repositories.session_repository import SessionRepository


class SessionService:
    """Manages sessions and messages."""

    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo

    async def create_session(self, user_id: str, metadata: Optional[dict] = None) -> Session:
        session = Session(
            session_id=f"session_{datetime.utcnow().timestamp()}",
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status="active",
            metadata=metadata or {},
            messages=[],
        )
        return await self.session_repo.create_session(session)

    async def append_message(self, session_id: str, role: str, content: str, tool_calls=None) -> None:
        session = await self.session_repo.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return
        message = Message(role=role, content=content, tool_calls=tool_calls)
        await self.session_repo.add_message(session_id, message.__dict__)

    async def get_session(self, session_id: str) -> Optional[Session]:
        return await self.session_repo.get_session(session_id)
