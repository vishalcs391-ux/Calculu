import uuid
from datetime import date, datetime
from sqlalchemy import Date, DateTime, Integer, Numeric, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProgressMetric(Base):
    __tablename__ = "progress_metrics"
    __table_args__ = (UniqueConstraint("user_id", "metric_date", name="uq_user_metric_date"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    metric_date: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    flashcards_reviewed: Mapped[int] = mapped_column(Integer, default=0)
    quizzes_taken: Mapped[int] = mapped_column(Integer, default=0)
    avg_quiz_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    study_minutes: Mapped[int] = mapped_column(Integer, default=0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
