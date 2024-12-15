from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    A configuration class for loading environment variables and settings.

    The class inherits from BaseSettings, which automatically reads from
    environment variables and (optionally) from a `.env` file. It provides
    a centralized configuration object that can be accessed throughout the application.

    Attributes:
        DB_URL (str): The database connection URL.
        JWT_SECRET (str): The secret key used to encode JWT tokens.
        JWT_ALGORITHM (str): The algorithm used for JWT encoding/decoding. Defaults to "HS256".
        JWT_EXPIRATION_SECONDS (int): The number of seconds after which a JWT expires. Defaults to 3600 (1 hour).

        MAIL_USERNAME (EmailStr): The username (email address) for the mail server.
        MAIL_PASSWORD (str): The password for the mail server.
        MAIL_FROM (EmailStr): The email address that appears as the sender.
        MAIL_PORT (int): The port used by the mail server.
        MAIL_SERVER (str): The mail server hostname or IP address.
        MAIL_FROM_NAME (str): The name that appears as the sender. Defaults to "Notes Service".

        CLD_NAME (str): The Cloudinary cloud name.
        CLD_API_KEY (int): The API key for Cloudinary.
        CLD_API_SECRET (str): The API secret for Cloudinary.
    """

    DB_URL: str = "postgresql+asyncpg://user:pass@localhost5432/bd"
    JWT_SECRET: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    MAIL_USERNAME: EmailStr = "name@domain.com"
    MAIL_PASSWORD: str = "password"
    MAIL_FROM: EmailStr = "name@domain.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp"
    MAIL_FROM_NAME: str = "Notes Service"

    CLD_NAME: str = "cloud_name"
    CLD_API_KEY: int = 1
    CLD_API_SECRET: str = "api_secret"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    model_config = ConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


config = Settings()
