from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:

    @staticmethod
    def register_user(db: Session, user_data: UserCreate):

        # Check if email already exists
        existing_user = UserRepository.get_by_email(
            db,
            user_data.email
        )

        if existing_user:
            raise ValueError("Email already registered")

        # Create user
        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
        )

        return UserRepository.create(db, user)
    
    
    @staticmethod
    def login_user(
        db: Session,
        email: str,
        password: str,
    ):
        # Find user by email
        user = UserRepository.get_by_email(db, email)

        # Check if user exists
        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        # Generate JWT token
        access_token = create_access_token(
            {
                "sub": user.email,
                "user_id": user.id,
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }