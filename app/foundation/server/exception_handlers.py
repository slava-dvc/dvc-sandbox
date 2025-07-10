import asyncio
from http import HTTPStatus
from json import JSONDecodeError

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from httpx import HTTPStatusError, StreamError
from starlette.requests import ClientDisconnect

from .config import AppConfig
from .dependencies import get_logger

__all__ = ['timeout_exception_handler', 'runtime_exception_handler', 'http_exception_handler',
           'request_validation_exception_handler']




def timeout_exception_handler(request: Request, exc: asyncio.TimeoutError):
    logger = get_logger(request)
    logger.warning("Request timeout")
    return JSONResponse(
        content={
            "error": {
                "code": HTTPStatus.REQUEST_TIMEOUT,
                "message": f"Timeout error during execution"
            }
        },
        status_code=HTTPStatus.REQUEST_TIMEOUT
    )


def http_exception_handler(request: Request, exc: HTTPStatusError):
    config: AppConfig = request.state.config
    logger = get_logger(request)
    logger.warning("Downstream HTTP error", labels={
        "status_code": exc.response.status_code,
        "content": exc.response.content
    })
    if config.debug:
        try:
            return Response(
                content=exc.response.content,
                status_code=exc.response.status_code,
                headers=exc.response.headers
            )
        except (JSONDecodeError, StreamError):
            pass

    return JSONResponse(
        content={
            "error": {
                "code": HTTPStatus.BAD_GATEWAY,
                "message": f"Http status {exc.response.status_code} from downstream http call"
            }
        },
        status_code=HTTPStatus.BAD_GATEWAY
    )


async def runtime_exception_handler(request: Request, exc: Exception):
    code = HTTPStatus.INTERNAL_SERVER_ERROR
    logger = get_logger(request)
    body = None
    try:
        body = await request.json()
    except ValueError:
        pass
    logger.error("Runtime exception", labels={
        "exception": str(exc),
        "body": body
    }, exc_info=exc)
    return JSONResponse(
        content={
            "error": {
                "code": code,
                "message": f"Exception {type(exc)} during execution"
            }
        },
        status_code=code
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    logger = get_logger(request)

    try:
        try:
            body = await request.json()
        except JSONDecodeError:
            body = await request.body()
            body = body.decode("utf-8")
    except (AttributeError, TypeError, ValueError, ClientDisconnect) as e:
        body = f"Unable to decode body: {e}"

    logger.warning("Validation error occurred", labels={
        "body": body,
        "errors": jsonable_encoder(exc.errors())
    })
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors())},
    )
    
