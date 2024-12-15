from fastapi import APIRouter, Depends, Request, UploadFile, File
from redis import Redis
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache.redis_cache import get_redis
from src.schemas.usesrs import User
from src.service.auth import get_current_user
from src.database.db import get_db
from src.service.upload_file import UploadFileService
from src.conf.config import config
from src.service.users import UserService
from src.service.users_cache import UserCacheService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/me", response_model=User, description="Limited by 5 requests per minute")
@limiter.limit("5 per minute")
async def me(request: Request, user: User = Depends(get_current_user)) -> User:
    """
    Retrieve the currently authenticated user's data.

    This endpoint is rate-limited to 5 requests per minute.

    Args:
        request (Request): The incoming HTTP request (used by the limiter for rate-limiting).
        user (User): The currently authenticated user, obtained from the authentication dependency.

    Returns:
        User: The authenticated user's data.
    """
    return user


@router.patch("/avatar", response_model=User, summary="Update User avatar")
async def update_avatar_user(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> User:
    """
    Update the authenticated user's avatar by uploading a new image to Cloudinary.

    Args:
        file (UploadFile): The uploaded image file.
        user (User): The currently authenticated user.
        db (AsyncSession): The asynchronous database session.
        redis (Redis): The redis connection

    Returns:
        User: The updated user object with the new avatar URL.
    """
    avatar_url = UploadFileService(
        config.CLD_NAME, config.CLD_API_KEY, config.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    user_cache_service = UserCacheService(redis)
    user_cache_service.set_user_to_cache(user)

    return user
