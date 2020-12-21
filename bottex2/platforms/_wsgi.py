import asyncio
from typing import AsyncIterator, Optional

from bottex2.handler import Request
from bottex2.keyboard import Keyboard
from bottex2.server import Transport


class WsgiTransport(Transport):
    def __init__(self):
        self._requests = asyncio.Queue()

    async def web_handler(self, environ, start_response):
        queue = asyncio.Queue()
        self._requests.put_nowait((environ, queue))
        response_headers = [('Content-type', 'text/plain')]
        response = await queue.get()
        start_response('200 OK', response_headers)
        return response

    async def listen(self) -> AsyncIterator[Request]:
        while True:
            request, queue = await self._requests.get()
            yield Request(text=request['PATH_INFO'],
                          raw=request,
                          __queue__=queue)

    async def send(self, request: Request,
                   text: Optional[str] = None,
                   kb: Optional[Keyboard] = None):
        request.__queue__.put_nowait(text.encode())
