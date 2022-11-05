from redis import Redis
from redis.exceptions import ConnectionError
from src.config import settings

try:
    redis_client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT
    )
    print("Connected to redis!")
except ConnectionError as e:
    print(e)

