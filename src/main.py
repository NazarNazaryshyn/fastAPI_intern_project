from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .config import settings
from src.router import router

import databases
import aioredis

Base.metadata.create_all(bind=engine)

app = FastAPI()


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
    await db.connect()
    app.state.redis = await aioredis.from_url('redis://redis:6379')


@app.on_event('shutdown')
async def shutdown():
    await db.disconnect()
    await app.state.redis.close()


@app.get("/")
async def root():
    return {"status": "working!"}


app.include_router(router, prefix='/user', tags=["user"])

