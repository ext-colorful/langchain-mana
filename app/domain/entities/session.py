"""Conversation session entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    """Conversation message."""

    role: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    tool_calls: Optional[list[dict]] = None


@dataclass
class Session:
    """Conversation session entity."""

    session_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    status: str
    metadata: dict | None = None
    messages: list[Message] | None = None
