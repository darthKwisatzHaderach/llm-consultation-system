from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import decode_and_validate


def _make_valid_token() -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "7",
        "role": "user",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def test_decode_extracts_sub_ok() -> None:
    token = _make_valid_token()
    payload = decode_and_validate(token)
    assert payload["sub"] == "7"


def test_garbage_token_raises() -> None:
    with pytest.raises(ValueError):
        decode_and_validate("not-even-a-jwt")
