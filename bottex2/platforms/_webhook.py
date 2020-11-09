import asyncio
from abc import ABC, abstractmethod

import aiohttp
import aiohttp.web

from bottex2.handler import Request
from bottex2.helpers import aiotools
from bottex2.logging import logger
from bottex2.receiver import Receiver


class InvalidRequest(ValueError):
    pass


class AioHttpReceiverMixin(Receiver, ABC):
    headers = {
        'Content-Type': 'application/json'
    }

    _host: str
    _port: int
    _path: str
    _requests_queue: asyncio.Queue  # type: asyncio.Queue[dict]

    async def web_handler(self, request: aiohttp.web.Request):
        try:
            dict_request = await request.json()
        except ValueError as e:
            logger.error(e, exc_info=True)
            return aiohttp.web.HTTPBadRequest(headers=self.headers)
        else:
            self._requests_queue.put_nowait(dict_request)
            return aiohttp.web.Response(status=200, headers=self.headers)

    @abstractmethod
    def parse_request(self, data: dict) -> Request:
        """
        :raises InvalidRequest
        """
        pass

    async def run_app(self):
        app = aiohttp.web.Application()
        app.router.add_post(self._path, self.web_handler)
        await aiohttp.web._run_app(app,
                                   host=self._host,
                                   port=self._port)

    async def listen(self):
        aiotools.create_task(self.run_app())
        while True:
            request = await self._requests_queue.get()
            try:
                yield self.parse_request(request)
            except InvalidRequest as e:
                logger.error(repr(e))
