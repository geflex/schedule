from bottex2.handler import Request
from bottex2.server import Transport


def test_custom_platform():
    class CustomTransport(Transport):
        async def listen(self):
            for _ in range(2):
                raw = {'text': 'message'}
                yield Request(text=raw['text'], raw=raw)

        async def send(self, request, text=None, kb=None):
            print(text)

    transport = CustomTransport()
