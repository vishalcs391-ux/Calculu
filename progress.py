from datetime import date
from pydantic import BaseModel


class ProgressDayOut(BaseModel):
    metric_date: date
    flashcards_reviewed: int
    quizzes_taken: int
    avg_quiz_score: float | None
    study_minutes: int
    streak_days: int

    class Config:
        from_attributes = True


class ProgressSummaryOut(BaseModel):
    total_study_minutes: int
    current_streak: int
    quizzes_taken: int
    avg_quiz_score: float | None
    days: list[ProgressDayOut]
