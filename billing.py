"""
Billing router — MVP placeholder for Stripe integration.
Plans: free | premium_monthly | student_yearly | school | teacher
Real checkout-session creation and webhook handling get wired in once
Stripe keys are available; the shape of the API is set now so the
frontend can be built against it today.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.deps import get_current_user
from app.models.user import User
from app.models.subscription import Subscription

router = APIRouter(prefix="/billing", tags=["billing"])

PLAN_CATALOG = {
    "free": {"name": "Free", "price": 0, "limits": "Limited uploads, flashcards, and quizzes per month"},
    "premium_monthly": {"name": "Premium (Monthly)", "price": 9.99, "limits": "Unlimited core features"},
    "student_yearly": {"name": "Student (Yearly)", "price": 59.0, "limits": "Unlimited core features, discounted"},
    "school": {"name": "School / College License", "price": None, "limits": "Seats-based, contact sales"},
    "teacher": {"name": "Teacher", "price": 14.99, "limits": "Class management tools (v2)"},
}


@router.get("/plans")
def list_plans():
    return PLAN_CATALOG


@router.post("/checkout")
def create_checkout_session(plan: str, user: User = Depends(get_current_user)):
    if plan not in PLAN_CATALOG:
        raise HTTPException(400, "Unknown plan")
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(501, "Stripe is not configured yet on this environment")
    # Placeholder: real implementation creates a stripe.checkout.Session
    # and returns {"checkout_url": session.url}
    return {"checkout_url": f"https://checkout.stripe.com/placeholder?plan={plan}"}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    # Placeholder: verify signature with settings.STRIPE_WEBHOOK_SECRET,
    # then update/create the Subscription row and User.plan accordingly.
    payload = await request.body()
    return {"received": True}
