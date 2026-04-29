from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import BaseHTTPException


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(BaseHTTPException)
    async def app_domain_errors(_request: Request, exc: BaseHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "code": exc.error_code,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_errors(_request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "code": "validation_error",
                "errors": jsonable_encoder(exc.errors()),
            },
        )
