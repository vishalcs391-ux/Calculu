"""
Rule-based study planner (MVP: simple even-distribution scheduler,
no AI call needed here — deterministic and cheap. AI can be layered
on top in v2 for smarter prioritization).
"""
from datetime import datetime, timedelta

from app.schemas.study import StudyPlanRequest


def build_plan(req: StudyPlanRequest) -> list[dict]:
    days_available = 14
    if req.exam_date:
        delta = (req.exam_date - datetime.utcnow()).days
        days_available = max(delta, 1)

    sessions = []
    topics = req.topics or ["General review"]
    for day_offset in range(days_available):
        topic = topics[day_offset % len(topics)]
        sessions.append({
            "topic": topic,
            "scheduled_at": datetime.utcnow() + timedelta(days=day_offset),
            "duration_minutes": req.minutes_per_day,
        })
    return sessions
