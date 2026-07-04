import uuid
from pydantic import BaseModel


class FlashcardOut(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    difficulty: str
    times_reviewed: int

    class Config:
        from_attributes = True


class FlashcardReviewIn(BaseModel):
    result: str  # "correct" | "incorrect"
