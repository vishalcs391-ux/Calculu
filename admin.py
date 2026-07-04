"""
Admin analytics router — basic usage monitoring for MVP.
Restricted to users with role == "admin" (see deps.require_admin).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from app.core.database import get_db
from app.deps import require_admin
from app.models.user import User
from app.models.source import Source
from app.models.quiz import Quiz
from app.models.subscription import Subscription

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def platform_stats(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    total_users = db.execute(select(func.count(User.id))).scalar_one()
    total_sources = db.execute(select(func.count(Source.id))).scalar_one()
    total_quizzes = db.execute(select(func.count(Quiz.id))).scalar_one()
    plan_breakdown = db.execute(
        select(User.plan, func.count(User.id)).group_by(User.plan)
    ).all()
    active_subs = db.execute(
        select(func.count(Subscription.id)).where(Subscription.status == "active")
    ).scalar_one()

    return {
        "total_users": total_users,
        "total_sources_uploaded": total_sources,
        "total_quizzes_generated": total_quizzes,
        "active_subscriptions": active_subs,
        "plan_breakdown": {plan: count for plan, count in plan_breakdown},
    }
