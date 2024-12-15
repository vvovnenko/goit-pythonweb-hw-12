from redis import Redis

from src.conf.config import config


def get_redis() -> Redis:
    return Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
