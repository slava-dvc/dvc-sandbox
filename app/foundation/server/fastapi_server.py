import logging

import uvicorn
from functools import cached_property

from .async_server import AsyncServer
from fastapi import FastAPI, Depends


__all__ = ['FastAPIServer']


class FastAPIServer(AsyncServer):

    @cached_property
    def app(self):
        app = FastAPI(
            debug=self.args['debug'],
            dependencies=self.dependencies(),
        )

        self.setup_app(app)
        return app

    def health_check(self):
        return True

    def dependencies(self):
        return [
            Depends(lambda: self.config),
            Depends(lambda: self.firestore_client),
            Depends(lambda: self.logging_client),
            Depends(lambda: self)
        ]

    def setup_app(self, app: FastAPI):
        pass

    def execute(self):
        with self.loop_executor:
            uvicorn.run(
                app=self.app,
                host="0.0.0.0",
                port=self.args['port'],
                access_log=not self.args['cloud'],
                log_level=logging.DEBUG if self.args['debug'] else logging.INFO,
                use_colors=True
            )
