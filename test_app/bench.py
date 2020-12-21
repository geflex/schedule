import asyncio
import time
import tracemalloc
from typing import Union, List

from bottex2.helpers import aiotools
from bottex2.platforms.py import PyMessage, PyServer, PyUserMiddleware
from schedule.main import setup_db
from test_app import logic


def rps(repeats, t):
    """
    Repeats per second.

    :param repeats: repeats per cycle
    :param t: cycle lenght in ms
    """
    if t == 0:
        return 0.0
    return 60 * repeats / t / 1000


py_server = PyServer(logic.router)


class Benchmark:
    def __init__(self,
                 server: PyServer,
                 repeats: Union[int, float] = 1E5):
        self.repeats = int(repeats)
        self.server = server
        self.queue = asyncio.Queue()  # type: asyncio.Queue[PyMessage]
        self.snapshots = []  # type: List[tracemalloc.Snapshot]
        self._last_id = 0

    async def send(self, text):
        self.server.recv_nowait(PyMessage(text, self.queue, self._last_id))
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
    setup_db()
    tracemalloc.start()
    benchmark = Benchmark(py_server, 1e3)
    py_server.add_handler_middleware(PyUserMiddleware)
    aiotools.run_async(py_server.serve_async(),
                       benchmark.serve(),
                       benchmark.bench())
