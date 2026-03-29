from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import (
    AuthTokenResponse,
    CurrentUserResponse,
    UserLoginRequest,
    UserSignupRequest,
)


class AuthService:
    def signup(self, db: Session, payload: UserSignupRequest) -> AuthTokenResponse:
        normalized_email = str(payload.email).strip().lower()
        existing_user = db.scalar(select(User).where(User.email == normalized_email))
        if existing_user is not None:
            raise ValueError("An account with this email already exists.")

        user = User(
            email=normalized_email,
            full_name=payload.full_name.strip(),
            password_hash=get_password_hash(payload.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token(user.id)
        return AuthTokenResponse(
            access_token=token,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
        )

    def login(self, db: Session, payload: UserLoginRequest) -> AuthTokenResponse:
        normalized_email = str(payload.email).strip().lower()
        user = db.scalar(select(User).where(User.email == normalized_email))
        if user is None or not verify_password(payload.password, user.password_hash):
            raise ValueError("Invalid email or password.")

        token = create_access_token(user.id)
        return AuthTokenResponse(
            access_token=token,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
        )

    def get_current_user_response(self, user: User) -> CurrentUserResponse:
        return CurrentUserResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
        )


auth_service = AuthService()
