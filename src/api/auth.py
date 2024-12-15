from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.usesrs import UserCreate, User
from src.schemas.auth import Token, RequestEmail
from src.service.auth import create_access_token, Hash, get_email_from_token
from src.service.email import send_email
from src.service.users import UserService
from src.database.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Registers a new user with the given user data, and sends an email for verification.

    Args:
        user_data (UserCreate): The data required to create a new user (username, email, password, etc.).
        background_tasks (BackgroundTasks): FastAPI's background task manager to send verification email asynchronously.
        request (Request): The incoming HTTP request object.
        db (AsyncSession): The asynchronous database session.

    Raises:
        HTTPException: If the email or username is already in use.

    Returns:
        User: The newly created user object.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )

    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)

    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Logs in an existing user using username and password, returning a JWT access token if successful.

    Args:
        form_data (OAuth2PasswordRequestForm): The OAuth2 form data containing username and password.
        db (AsyncSession): The asynchronous database session.

    Raises:
        HTTPException: If the username or password is incorrect, or if the user's email is not confirmed.

    Returns:
        Token: A dictionary containing the access token and token type (bearer).
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна адреса не підтверджена",
        )

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}", summary="Email confirmation")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirms a user's email using a token sent via email.

    Args:
        token (str): The token that was sent to the user’s email.
        db (AsyncSession): The asynchronous database session.

    Raises:
        HTTPException: If verification fails or the token is invalid.

    Returns:
        dict: A message indicating whether the email has been confirmed.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.is_confirmed:
        return {"message": "Your email has already been confirmed."}
    await user_service.confirmed_email(email)
    return {"message": "Your email has been confirmed."}


@router.post("/request_email", summary="Request email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Requests a new verification email to be sent to the user.

    Args:
        body (RequestEmail): The request body containing the user's email.
        background_tasks (BackgroundTasks): FastAPI's background task manager to send verification email asynchronously.
        request (Request): The incoming HTTP request object.
        db (AsyncSession): The asynchronous database session.

    Returns:
        dict: A message indicating if the email will be sent or if it is already confirmed.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user and user.is_confirmed:
        return {"message": "Your email has already been confirmed."}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation."}
