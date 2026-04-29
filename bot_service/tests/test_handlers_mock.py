from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fakeredis.aioredis import FakeRedis
from jose import jwt

from app.bot.handlers import text_message, token_cmd
from app.bot.redis_keys import jwt_storage_key
from app.bot import texts
from app.core.config import settings


def _jwt_string() -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "1",
        "role": "user",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


@pytest_asyncio.fixture
async def patched_redis(monkeypatch):
    redis = FakeRedis(decode_responses=True)
    monkeypatch.setattr("app.bot.handlers.get_redis", lambda: redis)
    yield redis


@pytest.mark.asyncio
async def test_token_command_saves_to_redis(patched_redis: FakeRedis) -> None:
    token = _jwt_string()
    message = AsyncMock()
    message.from_user = MagicMock(id=4242)
    message.answer = AsyncMock()

    command = MagicMock()
    command.args = token

    await token_cmd(message, command)

    key = jwt_storage_key(4242)
    assert await patched_redis.get(key) == token
    message.answer.assert_awaited()


@pytest.mark.asyncio
async def test_plain_text_without_token_skips_llm(monkeypatch, patched_redis: FakeRedis) -> None:
    mock_task = MagicMock()
    mock_task.delay = MagicMock()
    monkeypatch.setattr("app.bot.handlers.llm_request", mock_task)

    msg = AsyncMock()
    msg.from_user = MagicMock(id=11)
    msg.chat = MagicMock(id=220)
    msg.text = "привет без токена"
    msg.answer = AsyncMock()

    await text_message(msg)

    mock_task.delay.assert_not_called()
    ans = msg.answer.call_args.args[0]
    assert isinstance(ans, str)
    assert "Нет сохранённого токена" in ans


@pytest.mark.asyncio
async def test_plain_text_with_token_calls_celery_delay(monkeypatch, patched_redis: FakeRedis) -> None:
    token = _jwt_string()
    await patched_redis.set(jwt_storage_key(11), token)

    mock_task = MagicMock()
    mock_task.delay = MagicMock()
    monkeypatch.setattr("app.bot.handlers.llm_request", mock_task)

    msg = AsyncMock()
    uid = 11
    chat_id = 220
    msg.from_user = MagicMock(id=uid)
    msg.chat = MagicMock(id=chat_id)
    msg.text = "вопрос в LLM"
    msg.answer = AsyncMock()

    await text_message(msg)

    mock_task.delay.assert_called_once_with(chat_id, "вопрос в LLM")
    accept = texts.REQUEST_ACCEPTED
    msg.answer.assert_awaited()
    called = msg.answer.call_args.args[0]
    assert called == accept
