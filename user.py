import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    display_name: str | None
    role: str
    plan: str
    created_at: datetime

    class Config:
        from_attributes = True
