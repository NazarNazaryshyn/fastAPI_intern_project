import os
from dotenv import load_dotenv


load_dotenv()


class Settings:
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    HTTP_PASSWORD: str = os.getenv("HTTP_PASSWORD")
    HTTP_USER: str = os.getenv("HTTP_USER")

    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: str = os.getenv("REDIS_PORT")

    DOMAIN: str = os.getenv("DOMAIN")
    API_AUDIENCE: str = os.getenv("API_AUDIENCE")
    ALGORITHMS: str = os.getenv("ALGORITHMS")
    ISSUER: str = os.getenv("ISSUER")

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")


settings = Settings()

