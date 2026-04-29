from contextlib import asynccontextmanager

import pytest
from starlette.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.db.models  # noqa: F401
from app.api.deps import get_db
from app.api.error_handlers import register_error_handlers
from app.api.router import api_router
from app.db.base import Base
from fastapi import FastAPI


@pytest.fixture
def auth_client() -> TestClient:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async def override_get_db():
        async with session_factory() as session:
            yield session

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        try:
            yield
        finally:
            await engine.dispose()

    application = FastAPI(lifespan=lifespan)
    register_error_handlers(application)
    application.include_router(api_router)
    application.dependency_overrides[get_db] = override_get_db

    with TestClient(application) as client:
        yield client


def test_register_login_me_happy_path(auth_client: TestClient) -> None:
    reg = auth_client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "secret12"},
    )
    assert reg.status_code == 200
    body = reg.json()
    assert body["email"] == "user@example.com"
    assert "id" in body

    login = auth_client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "secret12"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = auth_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "user@example.com"


def test_negative_auth_flows(auth_client: TestClient) -> None:
    first = auth_client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "secret12"},
    )
    assert first.status_code == 200

    dup = auth_client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "otherpass12"},
    )
    assert dup.status_code == 409
    assert dup.json().get("code") == "user_already_exists"

    bad_login = auth_client.post(
        "/auth/login",
        data={"username": "dup@example.com", "password": "wrongpass"},
    )
    assert bad_login.status_code == 401
    assert bad_login.json().get("code") == "invalid_credentials"

    no_hdr = auth_client.get("/auth/me")
    assert no_hdr.status_code == 401
    assert no_hdr.json().get("code") == "invalid_token"

    bogus = auth_client.get("/auth/me", headers={"Authorization": "Bearer bogus.token.x"})
    assert bogus.status_code == 401
