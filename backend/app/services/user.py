"""
User service layer for business logic.
Handles user registration, authentication, profile management, and account operations.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User, AuthProvider
from app.utils.auth import hash_password, verify_password


class UserService:
    """Service class for user-related business logic."""

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            db: Database session
            email: User's email address

        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(
            User.email == email,
            User.deleted_at == None
        ).first()

    @staticmethod
    def create_user_with_email(
        db: Session,
        email: str,
        password: str,
        username: Optional[str] = None,
        display_name: Optional[str] = None
    ) -> User:
        """
        Create a new user with email/password authentication.

        Args:
            db: Database session
            email: User's email address
            password: Plain text password (will be hashed)
            username: Optional username
            display_name: Optional display name

        Returns:
            Created User object

        Raises:
            ValueError: If email is already registered
        """
        # Check if email already exists
        existing_user = UserService.get_user_by_email(db, email)
        if existing_user:
            raise ValueError("Email already registered")

        # Hash password
        hashed_password = hash_password(password)

        # Create user
        user = User(
            email=email,
            username=username,
            display_name=display_name or username or email.split('@')[0],
            auth_provider=AuthProvider.EMAIL,
            auth_provider_id=hashed_password,  # Store hashed password in auth_provider_id
            is_active=True,
            last_login_at=datetime.utcnow()
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.

        Args:
            db: Database session
            email: User's email address
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        # Get user by email
        user = db.query(User).filter(
            User.email == email,
            User.auth_provider == AuthProvider.EMAIL,
            User.is_active == True,
            User.deleted_at == None
        ).first()

        if not user:
            return None

        # Verify password (stored in auth_provider_id)
        if not verify_password(password, user.auth_provider_id):
            return None

        # Update last login time
        user.last_login_at = datetime.utcnow()
        db.commit()

        return user

    @staticmethod
    def update_user_profile(db: Session, user: User, update_data: dict) -> User:
        """
        Update user profile information.

        Args:
            db: Database session
            user: User object to update
            update_data: Dictionary of fields to update

        Returns:
            Updated User object
        """
        # Update only provided fields
        allowed_fields = ['username', 'display_name', 'avatar_url', 'age', 'gender']

        for field in allowed_fields:
            if field in update_data and update_data[field] is not None:
                setattr(user, field, update_data[field])

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update_user_settings(db: Session, user: User, settings_data: dict) -> User:
        """
        Update user notification settings.

        Args:
            db: Database session
            user: User object to update
            settings_data: Dictionary of settings to update

        Returns:
            Updated User object
        """
        # Update only provided settings
        allowed_settings = ['push_enabled', 'dnd_enabled', 'dnd_start_time', 'dnd_end_time']

        for setting in allowed_settings:
            if setting in settings_data and settings_data[setting] is not None:
                setattr(user, setting, settings_data[setting])

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def deactivate_user(db: Session, user: User) -> None:
        """
        Deactivate (soft delete) a user account.

        Args:
            db: Database session
            user: User object to deactivate
        """
        user.is_active = False
        user.deleted_at = datetime.utcnow()

        db.commit()
