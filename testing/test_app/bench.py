import sys; sys.path.extend(['D:\\Documents\\Code\\Python\\schedule'])

import asyncio
import time
from typing import Union

from bottex2.platforms.py import PyMessage, PyReceiver

from testing.test_app.main import bottex, setup_user_model


async def bench(receiver: PyReceiver, repeats: Union[int, float] = 1E5):
    repeats = int(repeats)
    back_queue = asyncio.Queue()
    while True:
        message = PyMessage('message text', back_queue)
        start = time.time()
        for _ in range(repeats):
            await receiver.recv(message)
            while not back_queue.empty():
                response = await back_queue.get()
        total = time.time() - start
        rps = 60 * repeats / total / 1000
        print(rps)
        # await asyncio.sleep(0.5)


py_receiver = PyReceiver()


async def main():
    bottex.add_receiver(py_receiver)
    await asyncio.gather(
        bench(py_receiver, 1E5),
        bottex.serve_async(),
    )


if __name__ == '__main__':
    setup_user_model()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
