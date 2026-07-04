"""
Source processing router: PDF upload and YouTube link ingestion.
Extraction happens synchronously for MVP simplicity; swap for a background
job queue (e.g. Celery/RQ) once files/videos get large — see roadmap.
"""
import os
import uuid as uuid_lib

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.deps import get_current_user
from app.models.user import User
from app.models.source import Source
from app.schemas.source import SourceOut, YouTubeSourceCreate
from app.services.pdf_service import extract_text_from_pdf
from app.services.youtube_service import extract_transcript

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("/pdf", response_model=SourceOut)
def upload_pdf(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_path = os.path.join(settings.UPLOAD_DIR, f"{uuid_lib.uuid4()}_{file.filename}")
    with open(saved_path, "wb") as f:
        f.write(file.file.read())

    source = Source(user_id=user.id, source_type="pdf", title=file.filename, original_ref=saved_path, status="processing")
    db.add(source)
    db.commit()
    db.refresh(source)

    try:
        text = extract_text_from_pdf(saved_path)
        source.raw_text = text
        source.status = "ready"
    except Exception as e:
        source.status = "failed"
        source.error_message = str(e)
    db.commit()
    db.refresh(source)
    return source


@router.post("/youtube", response_model=SourceOut)
def add_youtube_source(
    payload: YouTubeSourceCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    source = Source(
        user_id=user.id, source_type="youtube", title=payload.youtube_url,
        original_ref=payload.youtube_url, status="processing",
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    try:
        text = extract_transcript(payload.youtube_url)
        source.raw_text = text
        source.status = "ready"
    except Exception as e:
        source.status = "failed"
        source.error_message = str(e)
    db.commit()
    db.refresh(source)
    return source


@router.get("", response_model=list[SourceOut])
def list_sources(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Source).filter(Source.user_id == user.id).order_by(Source.created_at.desc()).all()
