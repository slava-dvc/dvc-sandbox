import asyncio
import logging
from http import HTTPStatus
from json import JSONDecodeError

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from google.cloud import logging as cloud_logging
from httpx import HTTPStatusError, StreamError
from starlette.requests import ClientDisconnect

from .config import AppConfig
from .dependencies import get_logger

__all__ = ['timeout_exception_handler', 'runtime_exception_handler', 'http_exception_handler',
           'request_validation_exception_handler']


logger = logging.getLogger(__name__)


def timeout_exception_handler(request: Request, exc: asyncio.TimeoutError):
    logger.warning(f"Timeout: {request.client.host} -> {request.method} {request.url}")
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
    logger.warning(f"Downstream http code {exc.response.status_code}: {request.client.host} -> {request.method} {request.url}")
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


def runtime_exception_handler(request: Request, exc: Exception):
    code = HTTPStatus.INTERNAL_SERVER_ERROR
    logger.error(f"Exception: {request.client.host} -> {request.method} {request.url}: {exc}", exc_info=exc)
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
    
