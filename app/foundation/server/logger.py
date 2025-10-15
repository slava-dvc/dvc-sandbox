import abc
import logging as python_logging
import os
import traceback
from typing import TYPE_CHECKING, Any
from fastapi import Request
try:
    from google.cloud import logging as google_logging
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    google_logging = None

if TYPE_CHECKING:
    from google.cloud import logging as google_logging

from fastapi.encoders import jsonable_encoder
from ..primitives import json

__all__ = ["Logger", "CloudLogger", "LocalLogger"]


class Logger:
    BLOCKLISTED_HEADERS = [
        "authorization",
        "cookie",
        "x-api-key",
    ]
    def __init__(self, request: Request = None):
        if request:
            path_parts = [p for p in request.url.path.split('/') if p ]
            self._name = "root" if not path_parts else '_'.join(path_parts)
            
            # Extract trace context from headers
            trace_header = request.headers.get('x-cloud-trace-context', '')
            if trace_header:
                trace_parts = trace_header.split('/')
                self._trace_id = trace_parts[0] if trace_parts else None
                self._span_id = trace_parts[1].split(';')[0] if len(trace_parts) > 1 else None
            else:
                self._trace_id = None
                self._span_id = None
            
            labels = {
                # "request_headers": {k:v for k,v in request.headers.items() if k.lower() not in self.BLOCKLISTED_HEADERS},
                "requestClient": str(request.client),
                "requestQueryParams": request.query_params,
                "requestUrl": str(request.url),
                "requestMethod": request.method,
                "handler": self._name,
            }
        else:
            self._name = "app"
            self._trace_id = None
            self._span_id = None
            labels = {"handler": self._name}
        
        self._labels = jsonable_encoder(labels)

    @abc.abstractmethod
    def debug(self, msg: str, labels: dict = None):
        pass

    @abc.abstractmethod
    def info(self, msg: str, labels: dict = None):
        pass

    @abc.abstractmethod
    def warning(self, msg: str, labels: dict = None):
        pass

    @abc.abstractmethod
    def error(self, msg: str, labels: dict = None, exc_info=None):
        pass


class CloudLogger(Logger):

    def __init__(
            self,
            logger_client: Any,  # google_logging.Client
            request: Request = None,
            project_id: str = None,
    ):
        super().__init__(request)
        self._project_id = project_id

        self._logger: Any = logger_client.logger(  # google_logging.Logger
            name="app",
        )

    def _make_log_data(self, msg: str, severity: str, labels: dict = None, exc_info=None):
        labels = self._labels | jsonable_encoder(labels or {})
        log_data = labels | {
            "message": msg,
            "severity": severity
        }
        
        # Add trace context for Google Cloud Logging
        if self._trace_id:
            log_data["trace"] = f"projects/{self._project_id}/traces/{self._trace_id}"
        if self._span_id:
            log_data["spanId"] = self._span_id
        
        if exc_info:
            log_data["excInfo"] = ''.join(traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__))
            
        return log_data

    def debug(self, msg: str, labels: dict = None):
        self._logger.log_struct(self._make_log_data(msg, "DEBUG", labels))

    def info(self, msg: str, labels: dict = None):
        self._logger.log_struct(self._make_log_data(msg, "INFO", labels))

    def warning(self, msg: str, labels: dict = None):
        self._logger.log_struct(self._make_log_data(msg, "WARNING", labels))

    def error(self, msg: str, labels: dict = None, exc_info=None):
        self._logger.log_struct(self._make_log_data(msg, "ERROR", labels, exc_info))


class LocalLogger(Logger):
    def __init__(self, request: Request = None):
        super().__init__(request)
        self._logger = python_logging.getLogger("app")

    def _make_log_data(self, msg: str, labels: dict = None):
        labels = self._labels | jsonable_encoder(labels or {})
        return '\n'.join([
            msg,
            json.dumps(labels)
        ])

    def debug(self, msg: str, labels: dict = None):
        self._logger.debug(self._make_log_data(msg, labels))

    def info(self, msg: str, labels: dict = None):
        self._logger.info(self._make_log_data(msg, labels))

    def warning(self, msg: str, labels: dict = None):
        self._logger.warning(self._make_log_data(msg, labels))

    def error(self, msg: str, labels: dict = None, exc_info=None):
        self._logger.error(self._make_log_data(msg, labels), exc_info=exc_info)
