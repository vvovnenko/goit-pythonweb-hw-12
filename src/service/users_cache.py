import json

from redis import Redis

from src.database.models import User


class UserCacheService:
    def __init__(self, redis_client: Redis, ttl: int = 5 * 60):
        """
        Ініціалізація сервісу кешування користувача.

        Args:
            redis_client: Підключення до Redis.
            ttl (int): Час життя кешу в секундах.
        """
        self.redis = redis_client
        self.ttl = ttl

    def get_user_from_cache(self, username: str) -> User | None:
        """
        Отримати дані користувача з кешу по username.

        Args:
            username (str): Ім'я користувача.

        Returns:
            User | None: Об'єкт користувача або None, якщо в кеші нема даних.
        """
        user_data = self.redis.get(f"user:{username}")
        if user_data:
            return User.from_dict(json.loads(user_data))
        return None

    def set_user_to_cache(self, user: User):
        """
        Зберегти дані користувача у кеш.

        Args:
            user (User): Об'єкт користувача для кешування.
        """
        self.redis.set(f"user:{user.username}", json.dumps(user.to_dict()), ex=self.ttl)
