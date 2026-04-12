import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
import re


# ── Request schemas ───────────────────────────────────────

class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    mobile: str
    password: str

    @field_validator("full_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Full name must be at least 2 characters")
        return v

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        digits = re.sub(r"[\s\-\+\(\)]", "", v)
        if not re.match(r"^\d{10,13}$", digits):
            raise ValueError("Enter a valid mobile number (10-13 digits)")
        return digits

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Response schemas ──────────────────────────────────────

class UserOut(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    mobile: str
    is_active: bool
    is_verified: bool
    vua: str | None
    aa_consent_id: str | None
    aa_consent_status: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int   # seconds
    user: UserOut


class MessageResponse(BaseModel):
    message: str
    success: bool = True
