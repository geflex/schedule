import sys; sys.path.extend(['D:\\Documents\\Code\\Python\\schedule'])

import tracemalloc
import asyncio
import time
from typing import Union, List

from bottex2.platforms.py import PyMessage, PyReceiver, PyUserHandlerMiddleware
from bottex2 import aiotools

from test_app import logic
from test_app.main import set_mongo_user_model


def rps(repeats, t):
    """
    Repeats per second.

    :param repeats: repeats per cycle
    :param t: cycle lenght in ms
    """
    if t == 0:
        return 0.0
    return 60 * repeats / t / 1000


py_receiver = PyReceiver()
py_receiver.set_handler(logic.router)


class Benchmark:
    def __init__(self,
                 receiver: PyReceiver,
                 repeats: Union[int, float] = 1E5):
        self.repeats = int(repeats)
        self.receiver = receiver
        self.queue = asyncio.Queue()  # type: asyncio.Queue[PyMessage]
        self.snapshots = []  # type: List[tracemalloc.Snapshot]
        self._last_id = 0

    async def send(self, text):
        self.receiver.recv_nowait(PyMessage(text, self.queue, self._last_id))
        self._last_id += 1

    async def serve(self):
        # ids = set()
        t = time.time()
        # while len(ids) != self.repeats:
        while True:
            response = await self.queue.get()
            # ids.add(response.response_id)
        # print(rps(self.repeats, time.time() - t))

    async def bench(self):
        for _ in range(self.repeats):
            await self.send('text')
            snap = tracemalloc.take_snapshot()
            self.snapshots.append(snap)

    def statistics(self):
        for prev_snap, snap in zip(self.snapshots, self.snapshots[1:]):
            stats = snap.compare_to(prev_snap, 'lineno')
            print()
            for stat in stats[:5]:
                print(stat)


if __name__ == '__main__':
    set_mongo_user_model()
    tracemalloc.start()
    benchmark = Benchmark(py_receiver, 1e3)
    py_receiver.add_handler_middleware(PyUserHandlerMiddleware)
    aiotools.run_async(py_receiver.serve_async(),
                       benchmark.serve(),
                       benchmark.bench())
