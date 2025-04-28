from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from errors.data_exeptions import NotFoundError, TransactionError, IncorrectFilterAppliedError
from errors.service_exeptions import (
    UserInactiveError,
    InvalidCredentialsError,
    UserDeletionIntegrityError,
    PermissionDenied,
    InvalidTokenTypeError,
)


def register_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_error(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"message": exc.msg})


    @app.exception_handler(TransactionError)
    async def transaction_error(request: Request, exc: TransactionError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"message": "Transaction Erros"})


    @app.exception_handler(UserInactiveError)
    async def inactive_error(request: Request, exc: UserInactiveError) -> JSONResponse:
        return JSONResponse(
            status_code=403, content={"message": exc.msg}
        )


    @app.exception_handler(InvalidCredentialsError)
    async def invalid_creadetial_error(request: Request, exc: InvalidCredentialsError) -> JSONResponse:
        return JSONResponse(
            status_code=401, content={"message": exc.msg}
        )


    @app.exception_handler(UserDeletionIntegrityError)
    async def user_delition_error(request: Request, exc: UserDeletionIntegrityError) -> JSONResponse:
        return JSONResponse(
            status_code=500, content={"message": exc.msg}
        )


    @app.exception_handler(PermissionDenied)
    async def permission_error(request: Request, exc: PermissionDenied) -> JSONResponse:
        return JSONResponse(
            status_code=403, content={"message": exc.msg}
        )


    @app.exception_handler(InvalidTokenTypeError)
    async def invalid_token_error(request: Request, exc: InvalidTokenTypeError) -> JSONResponse:
        return JSONResponse(
            status_code=401, content={"message": exc.msg}
        )
    

    @app.exception_handler(IncorrectFilterAppliedError)
    async def incorrect_filters_error(request: Request, exc: IncorrectFilterAppliedError) -> JSONResponse:
        return JSONResponse(
            status_code=500, content={"message": exc.msg}
        )