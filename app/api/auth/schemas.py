"""
Pydantic schemas for auth API (request/response validation).
"""
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Request body for user registration."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)


class UserLoginRequest(BaseModel):
    """Request body for login (username + password)."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class UserResponse(BaseModel):
    """Public user data returned by /auth/me and after login."""

    id: int
    email: str
    username: str
    is_active: bool

    model_config = {"from_attributes": True}
