from fastapi import HTTPException


class BaseHTTPException(HTTPException):
    status_code = 500
    detail = "Internal server error"
    error_code = "internal_error"

    def __init__(self, detail: str | None = None):
        super().__init__(status_code=self.status_code, detail=detail or self.detail)


class UserAlreadyExistsError(BaseHTTPException):
    status_code = 409
    detail = "User with this email already exists"
    error_code = "user_already_exists"


class InvalidCredentialsError(BaseHTTPException):
    status_code = 401
    detail = "Invalid email or password"
    error_code = "invalid_credentials"


class InvalidTokenError(BaseHTTPException):
    status_code = 401
    detail = "Invalid token"
    error_code = "invalid_token"


class TokenExpiredError(BaseHTTPException):
    status_code = 401
    detail = "Token expired"
    error_code = "token_expired"


class UserNotFoundError(BaseHTTPException):
    status_code = 404
    detail = "User not found"
    error_code = "user_not_found"


class PermissionDeniedError(BaseHTTPException):
    status_code = 403
    detail = "Permission denied"
    error_code = "permission_denied"
