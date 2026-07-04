import uuid
from datetime import datetime
from pydantic import BaseModel


class StudyPlanRequest(BaseModel):
    topics: list[str]
    exam_date: datetime | None = None
    minutes_per_day: int = 30


class StudySessionOut(BaseModel):
    id: uuid.UUID
    session_type: str
    topic: str | None
    scheduled_at: datetime | None
    duration_minutes: int | None
    status: str

    class Config:
        from_attributes = True


class TutorChatIn(BaseModel):
    message: str
    source_id: uuid.UUID | None = None  # optional context


class TutorChatOut(BaseModel):
    reply: str


class PracticeTestRequest(BaseModel):
    source_ids: list[uuid.UUID]
    num_questions: int = 15
    difficulty: str = "medium"
    duration_minutes: int = 30
