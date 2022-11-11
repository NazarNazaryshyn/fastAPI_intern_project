from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from src.user.models import Base
from .config import settings
from src.user.router import router
from src.auth.router import auth_router
from src.company.router import comp_router
from src.quiz.router import quiz_router
import databases
import aioredis
from fastapi.security import HTTPBearer
from src.database import async_session

app = FastAPI()
token_auth_scheme = HTTPBearer()

origins = [
    "http://localhost:8000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


db = databases.Database(settings.DATABASE_URL)


@app.on_event('startup')
async def startup():
    app.state.redis = await aioredis.from_url('redis://redis:6379')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@app.on_event('shutdown')
async def shutdown():
    await db.disconnect()
    await app.state.redis.close()


@app.get("/")
async def root():
    return {"status": "Working"}


app.include_router(router, prefix='/user', tags=["user"])
app.include_router(auth_router, prefix='/auth', tags=["auth"])
app.include_router(comp_router, prefix='/company', tags=["company"])
app.include_router(quiz_router, prefix='/quiz', tags=['quiz'])

