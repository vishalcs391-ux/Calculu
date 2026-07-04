"""
Rolls up study activity into daily progress_metrics rows and computes
a simple current streak for the dashboard.
"""
from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.progress_metric import ProgressMetric


def record_activity(db: Session, user_id, flashcards_reviewed=0, quizzes_taken=0, quiz_score=None, study_minutes=0):
    today = date.today()
    row = db.execute(
        select(ProgressMetric).where(ProgressMetric.user_id == user_id, ProgressMetric.metric_date == today)
    ).scalar_one_or_none()

    if not row:
        yesterday = db.execute(
            select(ProgressMetric).where(
                ProgressMetric.user_id == user_id, ProgressMetric.metric_date == today - timedelta(days=1)
            )
        ).scalar_one_or_none()
        streak = (yesterday.streak_days + 1) if yesterday else 1
        row = ProgressMetric(user_id=user_id, metric_date=today, streak_days=streak)
        db.add(row)

    row.flashcards_reviewed += flashcards_reviewed
    row.quizzes_taken += quizzes_taken
    row.study_minutes += study_minutes
    if quiz_score is not None:
        row.avg_quiz_score = (
            quiz_score if row.avg_quiz_score is None else round((row.avg_quiz_score + quiz_score) / 2, 2)
        )
    db.commit()
    db.refresh(row)
    return row
