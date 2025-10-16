import asyncio
from http import HTTPStatus

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI
from ..server.dependencies import get_logger


__all__ = ["RequestTimeoutMiddleware"]


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, timeout: int = 30):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try:
            return await asyncio.wait_for(call_next(request), timeout=self.timeout)
        except asyncio.TimeoutError as e:
            logger = get_logger(request)
            logger.warning(f"Request Timeout after {self.timeout}: {request.client.host} -> {request.method} {request.url}")
            return Response(status_code=HTTPStatus.GATEWAY_TIMEOUT)
