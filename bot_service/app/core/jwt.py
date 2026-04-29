from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import settings


def decode_and_validate(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_alg],
        )
    except ExpiredSignatureError as exc:
        raise ValueError("token expired") from exc
    except JWTError as exc:
        raise ValueError("invalid token") from exc
    if "sub" not in payload:
        raise ValueError("invalid token")
    return payload


def is_valid_token(token: str) -> bool:
    try:
        decode_and_validate(token)
    except ValueError:
        return False
    return True
