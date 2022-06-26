import asyncio
import logging

import uvicorn
from fastapi import FastAPI

logger = logging.getLogger()


class FastAPIServer:
    """
    Helper class for instantiating fast api server.

    """

    def __init__(self,
                 root_path: str = '',
                 http_path: int = 8080) -> None:

        self.root_path: str = root_path
        self.http_port: int = http_path

    def start_server(self, app: FastAPI) -> None:

        loop = asyncio.new_event_loop()

        config = uvicorn.Config(
            app=app,
            loop=loop,
            host="0.0.0.0",
            port=self.http_port,
            root_path=self.root_path,
            workers=1,
            access_log=True
        )

        server = uvicorn.Server(config)
        loop.run_until_complete(server.serve())
