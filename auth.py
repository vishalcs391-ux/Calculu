"""
Auth router — Firebase does the actual authentication (sign up / sign in
happen client-side via the Firebase SDK). This router just exposes
"who am I" so the frontend can fetch/refresh the profile after login.
"""
from fastapi import APIRouter, Depends

from app.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return user
