from fastapi import APIRouter, Depends, HTTPException, status
#from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import LoginRequest, Token
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return AuthService.register_user(db, user)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


# @router.post(
#     "/login",
#     response_model=Token,
# )
# def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db),
# ):
#     try:
#         return AuthService.login_user(
#             db=db,
#             email=form_data.username,
#             password=form_data.password,
#         )

#     except ValueError as e:
#         raise HTTPException(
#             status_code=401,
#             detail=str(e),
#         )

@router.post(
    "/login",
    response_model=Token,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        return AuthService.login_user(
            db=db,
            email=login_data.email,
            password=login_data.password,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user