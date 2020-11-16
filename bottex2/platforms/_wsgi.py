import asyncio
from abc import abstractmethod, ABC
from typing import AsyncIterator, Optional, Type, Iterable

from bottex2.chat import AbstractChat, Keyboard
from bottex2.handler import Request, HandlerMiddleware, Handler
from bottex2.receiver import Receiver


class AbstractServerChat(AbstractChat, ABC):
    @abstractmethod
    def flush(self):
        pass


class ServerChat(AbstractChat, ABC):
    def __init__(self, queue):
        self._queue = queue
        self._response = []

    def flush(self):
        self._queue.put_nowait([t.encode() for t in self._response])


class WsgiChat(ServerChat):
    def send_message(self,
                     text: Optional[str] = None,
                     kb: Optional[Keyboard] = None):
        self._response.append(text)


class WsgiReceiver(Receiver):
    def __init__(self, handler: Handler, middlewares: Iterable[Type[HandlerMiddleware]] = ()):
        super().__init__(handler, middlewares)
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
                          chat=WsgiChat(queue),
                          raw=request)
