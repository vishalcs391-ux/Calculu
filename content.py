"""
Content generation router: summary/notes, flashcards, quizzes.
This is where "source -> notes -> flashcards -> quiz" pipeline lives.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.source import Source
from app.models.summary import Summary
from app.models.flashcard import Flashcard
from app.models.quiz import Quiz
from app.schemas.summary import SummaryOut
from app.schemas.flashcard import FlashcardOut, FlashcardReviewIn
from app.schemas.quiz import QuizOut, QuizSubmitIn
from app.services.ai.ai_service import ai_service
from app.services.flashcard_service import generate_flashcards_for_summary, review_flashcard
from app.services.quiz_service import generate_quiz_for_summary, score_quiz
from app.services.progress_service import record_activity

router = APIRouter(prefix="/content", tags=["content"])


def _get_owned_source(db: Session, source_id: uuid.UUID, user: User) -> Source:
    source = db.query(Source).filter(Source.id == source_id, Source.user_id == user.id).first()
    if not source:
        raise HTTPException(404, "Source not found")
    if source.status != "ready":
        raise HTTPException(409, f"Source is not ready yet (status={source.status})")
    return source


@router.post("/sources/{source_id}/summarize", response_model=SummaryOut)
def summarize_source(source_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    source = _get_owned_source(db, source_id, user)
    result = ai_service.summarize(source.raw_text)
    summary = Summary(source_id=source.id, user_id=user.id, content_md=result["content_md"], key_points=result.get("key_points"))
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary


@router.post("/summaries/{summary_id}/flashcards", response_model=list[FlashcardOut])
def create_flashcards(summary_id: uuid.UUID, count: int = 12, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    summary = db.query(Summary).filter(Summary.id == summary_id, Summary.user_id == user.id).first()
    if not summary:
        raise HTTPException(404, "Summary not found")
    return generate_flashcards_for_summary(db, summary.id, user.id, summary.content_md, count=count)


@router.get("/summaries/{summary_id}/flashcards", response_model=list[FlashcardOut])
def list_flashcards(summary_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Flashcard).filter(Flashcard.summary_id == summary_id, Flashcard.user_id == user.id).all()


@router.post("/flashcards/{card_id}/review", response_model=FlashcardOut)
def review_card(card_id: uuid.UUID, payload: FlashcardReviewIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    card = db.query(Flashcard).filter(Flashcard.id == card_id, Flashcard.user_id == user.id).first()
    if not card:
        raise HTTPException(404, "Flashcard not found")
    card = review_flashcard(db, card, payload.result)
    record_activity(db, user.id, flashcards_reviewed=1)
    return card


@router.post("/summaries/{summary_id}/quiz", response_model=QuizOut)
def create_quiz(summary_id: uuid.UUID, num_questions: int = 10, difficulty: str = "medium", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    summary = db.query(Summary).filter(Summary.id == summary_id, Summary.user_id == user.id).first()
    if not summary:
        raise HTTPException(404, "Summary not found")
    return generate_quiz_for_summary(db, summary.id, user.id, summary.content_md, num_questions, difficulty)


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizOut)
def submit_quiz(quiz_id: uuid.UUID, payload: QuizSubmitIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == user.id).first()
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    quiz.score = score_quiz(quiz, payload.answers)
    quiz.attempts += 1
    db.commit()
    db.refresh(quiz)
    record_activity(db, user.id, quizzes_taken=1, quiz_score=quiz.score)
    return quiz
