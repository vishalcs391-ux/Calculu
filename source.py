import uuid
from datetime import datetime
from pydantic import BaseModel


class YouTubeSourceCreate(BaseModel):
    youtube_url: str


class SourceOut(BaseModel):
    id: uuid.UUID
    source_type: str
    title: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
