import asyncio
from abc import ABC, abstractmethod

import aiohttp
import aiohttp.web

from bottex2 import aiotools
from bottex2.handler import Request
from bottex2.receiver import Receiver


class WebHookReceiverMixin(Receiver, ABC):
    headers = {
        'Content-Type': 'application/json'
    }

    _host: str
    _port: int
    _path: str
    _requests_queue = asyncio.Queue()  # type: asyncio.Queue[dict]

    async def web_handler(self, request: aiohttp.web.Request):
        dict_request = await request.json()
        self._requests_queue.put_nowait(dict_request)
        return aiohttp.web.Response(status=200, headers=self.headers)

    async def serve_web(self):
        app = aiohttp.web.Application()
        app.router.add_get(self._path, self.web_handler)
        await aiohttp.web._run_app(app, host=self._host, port=self._port)

    @abstractmethod
    def yielder(self, data: dict) -> Request:
        pass

    async def listen(self):
        aiotools.create_task(self.serve_web())
        while True:
            request = await self._requests_queue.get()
            yield self.yielder(request)
