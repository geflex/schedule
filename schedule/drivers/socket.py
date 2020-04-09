import time
import asyncio

import bottex
from bottex.drivers import Driver, Text, Request
from bottex.views import viewnames


class SocketDriver(Driver):
    def create_kb(self, buttons):
        return

    def get_handler(self, name):
        return viewnames[name]

    site_name = '_socket'

    def __init__(self, host, port):
        self.host, self.port = host, port
        self.user = self.get_user(None)

    async def send(self, response, user):
        if hasattr(response, 'writer'):
            for msg in response:
                if isinstance(msg, Text) and msg.text:
                    response.writer.write((msg.text.replace('\n', '\n\r')+'\n\r').encode())
            await response.writer.drain()

    async def listen(self):
        yield

    async def handle_response(self, reader, writer):
        while True:
            try:
                line = await reader.readline()
            except ConnectionResetError:
                bottex.logger.info('connection closed')
                break
            line = line.decode().rstrip()
            t = time.time()
            bottex.logger.debug(f'New message {line!r} from {self.user!r}')
            request = Request(self.user, line)
            handler = self.get_handler(self.user.last_view)
            response = handler(request)
            response.writer = writer
            bottex.logger.debug(f'Message time {time.time() - t}')
            try:
                await self.send(response, self.user)
            except ConnectionResetError:
                bottex.logger.info('connection closed')
                break

    async def run(self):
        bottex.logger.debug(f'Listening on {self.host}:{self.port}')
        server = await asyncio.start_server(self.handle_response, self.host, self.port)
        await server.serve_forever()
