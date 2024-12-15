from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.conf.config import config
from src.service.auth import create_email_token, create_reset_password_token

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME=config.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Sends a verification email to the provided email address with a token for confirming the user's email.

    Args:
        email (EmailStr): The recipient's email address.
        username (str): The username of the user receiving the verification email.
        host (str): The host URL of the application, used to construct the verification link.

    Raises:
        ConnectionErrors: If an error occurs while connecting to the email server.

    Returns:
        None
    """
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_password_email(
    email: EmailStr, username: str, hashed_password: str, host: str
):
    try:
        reset_password_token = create_reset_password_token(email, hashed_password)

        message = MessageSchema(
            subject="Reset password",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": reset_password_token,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(err)
