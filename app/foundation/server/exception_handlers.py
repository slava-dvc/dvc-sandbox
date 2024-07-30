import logging
import asyncio

from http import HTTPStatus
from json import JSONDecodeError

from fastapi.responses import JSONResponse, Response
from httpx import HTTPStatusError, ResponseNotRead, StreamError
from fastapi import Request
from .config import AppConfig


__all__ = ['timeout_exception_handler', 'runtime_exception_handler', 'http_exception_handler']


config = AppConfig()

def timeout_exception_handler(request: Request, exc: asyncio.TimeoutError):
    logging.warning(f"Timeout: {request.client.host} -> {request.method} {request.url}")
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
    logging.warning(f"Downstream http code {exc.response.status_code}: {request.client.host} -> {request.method} {request.url}")
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
    logging.error(f"Exception: {request.client.host} -> {request.method} {request.url} -> {exc}", exc_info=exc)
    return JSONResponse(
        content={
            "error": {
                "code": code,
                "message": f"Exception {type(exc)} during execution"
            }
        },
        status_code=code
    )