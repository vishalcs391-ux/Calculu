import uuid
from datetime import datetime
from pydantic import BaseModel


class SummaryOut(BaseModel):
    id: uuid.UUID
    source_id: uuid.UUID
    content_md: str
    key_points: list[str] | None
    created_at: datetime

    class Config:
        from_attributes = True
