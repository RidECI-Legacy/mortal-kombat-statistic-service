import redis.asyncio as redis
from src.rideci.core.settings import settings

class RedisConfig:
    _instance = None

    @classmethod
    def get_connection(cls) -> redis.Redis:
        if cls._instance is None:
            cls._instance = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                ssl=True, 
                ssl_cert_reqs=None, 
                decode_responses=True
            )
        return cls._instance