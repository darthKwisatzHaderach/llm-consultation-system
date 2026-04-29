from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.infra.redis import close_redis


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        yield
    finally:
        await close_redis()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
