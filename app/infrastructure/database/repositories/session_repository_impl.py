"""Session repository implementation."""

from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.session import Message, Session
from app.domain.repositories.session_repository import SessionRepository
from app.infrastructure.database.models.session_models import SessionModel


class SessionRepositoryImpl(SessionRepository):
    """SQLAlchemy implementation for sessions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(self, session_entity: Session) -> Session:
        model = SessionModel(
            session_id=session_entity.session_id,
            user_id=session_entity.user_id,
            status=session_entity.status,
            metadata_json=session_entity.metadata,
            messages=[m.__dict__ for m in session_entity.messages or []],
        )
        self.session.add(model)
        await self.session.commit()
        return session_entity

    async def get_session(self, session_id: str) -> Optional[Session]:
        stmt = select(SessionModel).where(SessionModel.session_id == session_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def update_session(self, session_entity: Session) -> Session:
        stmt = (
            update(SessionModel)
            .where(SessionModel.session_id == session_entity.session_id)
            .values(
                status=session_entity.status,
                metadata_json=session_entity.metadata,
                messages=[m.__dict__ for m in session_entity.messages or []],
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return session_entity

    async def add_message(self, session_id: str, message: dict) -> None:
        session = await self.get_session(session_id)
        if not session:
            return
        messages = session.messages or []
        messages.append(message)
        await self.session.execute(
            update(SessionModel)
            .where(SessionModel.session_id == session_id)
            .values(messages=messages)
        )
        await self.session.commit()

    async def list_sessions(self, user_id: str) -> Iterable[Session]:
        stmt = select(SessionModel).where(SessionModel.user_id == user_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: SessionModel) -> Session:
        messages = [Message(**msg) for msg in (model.messages or [])]
        return Session(
            session_id=model.session_id,
            user_id=model.user_id,
            status=model.status,
            metadata=model.metadata_json,
            messages=messages,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
