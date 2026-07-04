"""
Business logic for flashcards: generation (via AIService) + simple
spaced-repetition scheduling on review.
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.flashcard import Flashcard
from app.services.ai.ai_service import ai_service

# Very simple spaced-repetition intervals (days), MVP-level — not full SM-2.
INTERVALS = {"again": 0, "correct_easy": 4, "correct_medium": 2, "correct_hard": 1, "incorrect": 0}


def generate_flashcards_for_summary(db: Session, summary_id, user_id, notes_md: str, count: int = 12) -> list[Flashcard]:
    raw_cards = ai_service.generate_flashcards(notes_md, count=count)
    cards = []
    for c in raw_cards:
        card = Flashcard(
            summary_id=summary_id,
            user_id=user_id,
            question=c["question"],
            answer=c["answer"],
            difficulty=c.get("difficulty", "medium"),
        )
        db.add(card)
        cards.append(card)
    db.commit()
    for card in cards:
        db.refresh(card)
    return cards


def review_flashcard(db: Session, card: Flashcard, result: str) -> Flashcard:
    card.times_reviewed += 1
    card.last_result = result
    if result == "correct":
        days = {"easy": 4, "medium": 2, "hard": 1}.get(card.difficulty, 2)
    else:
        days = 0  # show again today
    card.next_review_at = datetime.utcnow() + timedelta(days=days)
    db.commit()
    db.refresh(card)
    return card
