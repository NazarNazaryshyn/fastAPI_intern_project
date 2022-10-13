from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
import postgres


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


@app.on_event("startup")
async def startup():
    await postgres.connect()
    await redis.connect()


@app.on_event("shutdown")
async def startup():
    await postgres.disconnect()
    await redis.disconnect()


@app.get("/")
async def root():
    return {"status": "Working!"}


