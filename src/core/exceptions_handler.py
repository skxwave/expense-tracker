from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from src.core.exceptions import (
    DomainException,
    EntityNotFoundError,
    EntityAlreadyExistsError,
    InvalidCredentialsError,
)


def add_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(
        request: Request,
        exc: EntityNotFoundError,
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message},
        )

    @app.exception_handler(EntityAlreadyExistsError)
    async def entity_already_exists_handler(
        request: Request,
        exc: EntityAlreadyExistsError,
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request,
        exc: InvalidCredentialsError,
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message},
        )
