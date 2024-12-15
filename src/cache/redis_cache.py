from redis import Redis


def get_redis() -> Redis:
    return Redis(host="localhost", port=6379, db=0)
