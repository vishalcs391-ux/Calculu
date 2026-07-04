"""
Firebase Authentication verification.

Frontend signs the user in with Firebase Auth (email/password or Google),
gets an ID token, and sends it as: Authorization: Bearer <id_token>
This module verifies that token on every protected request.
"""
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from fastapi import HTTPException, status

from app.core.config import settings

_firebase_app = None


def init_firebase():
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app
    if settings.FIREBASE_SERVICE_ACCOUNT_JSON:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
        _firebase_app = firebase_admin.initialize_app(cred)
    else:
        # Falls back to Application Default Credentials (useful in some cloud hosts)
        _firebase_app = firebase_admin.initialize_app()
    return _firebase_app


def verify_firebase_token(id_token: str) -> dict:
    """Returns decoded token claims (uid, email, ...) or raises 401."""
    init_firebase()
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )
