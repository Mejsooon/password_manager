import logging

import mysql.connector
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import auth, passwords
from app.core.exceptions import AppException
from app.core.logging_config import configure_logging


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="Password Manager",
        description="REST API for Password Manager",
        version="1.0.0",
    )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(
            "%s %s -> %s",
            request.method,
            request.url.path,
            exc.detail,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(mysql.connector.Error)
    async def database_exception_handler(
        request: Request,
        exc: mysql.connector.Error,
    ):
        logger.error(
            "Database error on %s %s: %s",
            request.method,
            request.url.path,
            exc,
        )

        return JSONResponse(
            status_code=503,
            content={"detail": "Database service unavailable"},
        )

    app.include_router(auth.router)
    app.include_router(passwords.router)

    return app


app = create_app()


@app.get("/", tags=["root"])
def root():
    return {"message": "Password Manager is working"}