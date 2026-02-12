"""
User API endpoints for authentication and profile management.
Handles registration, login, profile operations, and account management.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    UserUpdate,
    UserSettingsUpdate
)
from app.services.user import UserService
from app.utils.auth import create_access_token, get_current_user


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email and password.

    Args:
        request: Registration data (email, password, optional username/display_name)
        db: Database session

    Returns:
        TokenResponse with access token and user information

    Raises:
        HTTPException 400: If email is already registered
    """
    try:
        # Create user
        user = UserService.create_user_with_email(
            db=db,
            email=request.email,
            password=request.password,
            username=request.username,
            display_name=request.display_name
        )

        # Generate access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        # Calculate expires_in (in seconds)
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            user=UserResponse.from_orm(user)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
def login_user(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.

    Args:
        request: Login credentials (email, password)
        db: Database session

    Returns:
        TokenResponse with access token and user information

    Raises:
        HTTPException 401: If credentials are incorrect
    """
    # Authenticate user
    user = UserService.authenticate_user(
        db=db,
        email=request.email,
        password=request.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    # Calculate expires_in (in seconds)
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's information.

    Args:
        current_user: Current authenticated user (from JWT token)

    Returns:
        UserResponse with user information
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.

    Args:
        update_data: Profile fields to update
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserResponse with updated user information
    """
    # Convert Pydantic model to dict, excluding None values
    update_dict = update_data.dict(exclude_unset=True)

    # Update profile
    updated_user = UserService.update_user_profile(
        db=db,
        user=current_user,
        update_data=update_dict
    )

    return UserResponse.from_orm(updated_user)


@router.put("/me/settings", response_model=UserResponse)
def update_user_settings(
    settings_data: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's notification settings.

    Args:
        settings_data: Notification settings to update
        current_user: Current authenticated user
        db: Database session

    Returns:
        UserResponse with updated user information
    """
    # Convert Pydantic model to dict, excluding None values
    settings_dict = settings_data.dict(exclude_unset=True)

    # Update settings
    updated_user = UserService.update_user_settings(
        db=db,
        user=current_user,
        settings_data=settings_dict
    )

    return UserResponse.from_orm(updated_user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete (deactivate) current user's account.
    This is a soft delete - data is retained but account is deactivated.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        204 No Content
    """
    UserService.deactivate_user(db=db, user=current_user)
    return None
