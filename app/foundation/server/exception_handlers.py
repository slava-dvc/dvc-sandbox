import asyncio
import sys
from http import HTTPStatus
from json import JSONDecodeError
from typing import Union

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from httpx import HTTPStatusError, StreamError, ReadError, ConnectError
from pydantic import ValidationError

from .config import AppConfig
from .dependencies import get_logger

__all__ = ['timeout_exception_handler', 'runtime_exception_handler', 'http_exception_handler',
           'http_connection_exception_handler', 'request_validation_exception_handler']


# Mapping downstream HTTP status codes to our service response codes
DOWNSTREAM_STATUS_MAPPING = {
    # Authentication/authorization issues - our service misconfiguration
    401: HTTPStatus.INTERNAL_SERVER_ERROR,
    403: HTTPStatus.INTERNAL_SERVER_ERROR,
    
    # Operational client errors - dependency issues
    404: HTTPStatus.SERVICE_UNAVAILABLE,
    429: HTTPStatus.SERVICE_UNAVAILABLE,
    
    # All 5xx errors - downstream service issues
    **{status: HTTPStatus.SERVICE_UNAVAILABLE for status in range(500, 600)}
}


async def request_body(request: Request):
    body = None
    if request.method in ['POST', 'PUT', 'PATCH']:
        try:
            body = await request.json()
        except JSONDecodeError:
            body = await request.body()
            if body:
                body = body.decode("utf-8")
        except ValueError:
            pass
    if body and isinstance(body, (dict, str)) and sys.getsizeof(body) < 1024 * 1024:
        return body
    return None


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


async def http_exception_handler(request: Request, exc: HTTPStatusError):
    config: AppConfig = request.state.config
    logger = get_logger(request)
    logger.warning("Downstream HTTP error", labels={
        "downstream": {
            "status_code": exc.response.status_code,
            "content": exc.response.content
        },
        "body": await request_body(request),
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

    # Map downstream status to appropriate response status
    response_status = DOWNSTREAM_STATUS_MAPPING.get(
        exc.response.status_code, 
        exc.response.status_code  # Pass through unmapped 4xx client errors
    )
    
    return JSONResponse(
        content={
            "error": {
                "code": response_status,
                "message": f"Http status {exc.response.status_code} from downstream http call"
            }
        },
        status_code=response_status
    )


def http_connection_exception_handler(request: Request, exc: Union[ReadError, ConnectError]):
    logger = get_logger(request)
    logger.warning("Downstream HTTP connection error", labels={
        "exceptionType": type(exc).__name__,
        "exception": str(exc)
    })

    return JSONResponse(
        content={
            "error": {
                "code": HTTPStatus.BAD_GATEWAY,
                "message": f"Connection error to downstream service: {type(exc).__name__}"
            }
        },
        status_code=HTTPStatus.BAD_GATEWAY
    )


async def runtime_exception_handler(request: Request, exc: Exception):
    code = HTTPStatus.INTERNAL_SERVER_ERROR
    logger = get_logger(request)
    logger.error("Runtime exception", labels={
        "body": await request_body(request),
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


async def validation_exception_handler(request: Request, exc: ValidationError):
    logger = get_logger(request)
    logger.error("Pydantic validation error", exc_info=exc, labels={
        "errors": jsonable_encoder(exc.errors()),
        "body": await request_body(request),
    })

    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    logger = get_logger(request)

    logger.warning("Validation error occurred", labels={
        "body": await request_body(request),
        "errors": jsonable_encoder(exc.errors())
    })
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors())},
    )
