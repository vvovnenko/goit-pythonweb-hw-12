from datetime import datetime, timedelta, UTC, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.cache.redis_cache import get_redis
from src.database.db import get_db
from src.conf.config import config
from src.database.models import User, UserRole
from src.service.users import UserService
from src.service.users_cache import UserCacheService


class Hash:
    """
    A utility class for hashing and verifying passwords using bcrypt.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a given plain-text password against a hashed password.

        Args:
            plain_password (str): The plain-text password to verify.
            hashed_password (str): The previously hashed password to compare against.

        Returns:
            bool: True if the plain password matches the hashed password, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hashes a plain-text password using bcrypt.

        Args:
            password (str): The plain-text password to hash.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Creates a new JWT access token.

    Args:
        data (dict): The payload data to include in the token.
        expires_delta (Optional[int]): The number of seconds until the token expires. If not provided, uses the default from config.JWT_EXPIRATION_SECONDS.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=config.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> User:
    """
    Retrieves the currently authenticated user based on the provided JWT token.

    Args:
        token (str): The JWT access token extracted from the Authorization header.
        db (AsyncSession): The database session dependency.
        redis (Redis): The redis connection

    Raises:
        HTTPException: If the credentials are invalid or the token cannot be validated.

    Returns:
        User: The user object corresponding to the token's subject (username).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    # Отримаємо користувача з кешу
    user_cache_service = UserCacheService(redis)
    user = user_cache_service.get_user_from_cache(username)
    if user:
        return user

    # Отримаємо користувача з бази даних
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception

    # Збережемо користувача у кеш
    user_cache_service.set_user_to_cache(user)

    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
    return current_user


def create_email_token(data: dict) -> str:
    """
    Creates a token specifically for email-related workflows (such as email verification).

    Args:
        data (dict): The payload data to include in the token.

    Returns:
        str: The encoded JWT token with an expiration of 7 days.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire})
    token = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str) -> str:
    """
    Extracts the email address from a given JWT token.

    Args:
        token (str): The token from which to extract the email address.

    Raises:
        HTTPException: If the token is invalid or cannot be decoded.

    Returns:
        str: The email address contained in the token.
    """
    try:
        payload = jwt.decode(
            token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Incorrect token.",
        )


def create_reset_password_token(email: EmailStr, hashed_password: str) -> str:
    """
    Create a reset password token for a given email and hashed password.

    This function generates a JWT token containing the user's email and hashed password.
    The token can be used later to reset the user's password without requiring the user
    to log in again.

    Args:
        email (EmailStr): The email address of the user who requested the password reset.
        hashed_password (str): The hashed password associated with the user.

    Returns:
        str: The JWT token containing the user's email and hashed password.
    """
    return create_access_token({"sub": email, "password": hashed_password})


async def get_email_and_password_from_token(token: str) -> dict:
    """
    Extract the email and password from a given JWT token.

    This function decodes a JWT token expected to contain "sub" and "password" fields,
    where "sub" should be the user's email address and "password" the hashed password.

    Args:
        token (str): The JWT token to decode.

    Raises:
        HTTPException: If the token is invalid or cannot be decoded.

    Returns:
        dict: A dictionary containing the user's email and hashed password in the format:
              {"email": <email>, "password": <hashed_password>}
    """
    try:
        payload = jwt.decode(
            token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )
        email = payload["sub"]
        password = payload["password"]
        return {"email": email, "password": password}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Incorrect token.",
        )
