"""
Auth business logic: registration, login, user lookup.
"""
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.models import User
from app.api.auth.schemas import UserRegisterRequest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def register_user(session: AsyncSession, payload: UserRegisterRequest) -> User:
    """
    Create a new user. Raises HTTPException if email or username already exists.
    """
    # Check existing email
    result = await session.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    # Check existing username
    result = await session.execute(select(User).where(User.username == payload.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, username: str, password: str) -> User | None:
    """Return user if credentials are valid, else None."""
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def create_token_for_user(user: User) -> str:
    """Create JWT access token for the given user."""
    settings = get_settings()
    return create_access_token(
        subject=user.id,
        expires_delta=None,  # use default from settings
    )


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    """Fetch user by primary key."""
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
