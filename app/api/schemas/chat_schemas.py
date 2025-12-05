"""Schemas for chat endpoints."""

from pydantic import BaseModel, Field


class ChatProcessRequest(BaseModel):
    text: str = Field(..., description="User input text")
    user_id: str | None = Field(None, description="User identifier")
    session_id: str | None = Field(None, description="Session identifier")


class ChatProcessResponse(BaseModel):
    content: str
    model: str
    usage: dict
