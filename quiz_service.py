"""
Business logic for quizzes: generation + scoring.
"""
from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.services.ai.ai_service import ai_service


def generate_quiz_for_summary(db: Session, summary_id, user_id, notes_md: str, num_questions: int, difficulty: str) -> Quiz:
    questions = ai_service.generate_quiz(notes_md, num_questions=num_questions, difficulty=difficulty)
    quiz = Quiz(
        summary_id=summary_id,
        user_id=user_id,
        title="Quiz",
        questions=questions,
        difficulty=difficulty,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


def score_quiz(quiz: Quiz, answers: list[int]) -> float:
    correct = sum(
        1 for i, q in enumerate(quiz.questions)
        if i < len(answers) and answers[i] == q["correct_index"]
    )
    return round((correct / len(quiz.questions)) * 100, 2) if quiz.questions else 0.0
