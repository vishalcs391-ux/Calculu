import uuid
from pydantic import BaseModel


class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct_index: int
    explanation: str


class QuizOut(BaseModel):
    id: uuid.UUID
    title: str
    questions: list[QuizQuestion]
    difficulty: str
    score: float | None

    class Config:
        from_attributes = True


class QuizSubmitIn(BaseModel):
    answers: list[int]  # selected option index per question
