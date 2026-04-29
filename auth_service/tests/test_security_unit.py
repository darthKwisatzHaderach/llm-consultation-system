from app.core.config import settings
from app.core.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hash_verify_and_negative():
    pwd = "my_secret_password"
    h = hash_password(pwd)
    assert h != pwd
    assert verify_password(pwd, h) is True
    assert verify_password("wrong", h) is False


def test_jwt_contains_expected_claims_and_roundtrip():
    token = create_access_token(sub="42", role="admin")
    payload = decode_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "admin"
    assert isinstance(payload["iat"], int)
    assert isinstance(payload["exp"], int)
    span_sec = payload["exp"] - payload["iat"]
    assert 0 < span_sec <= settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60 + 5
