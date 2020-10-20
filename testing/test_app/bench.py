import sys; sys.path.extend(['D:\\Documents\\Code\\Python\\schedule'])

import tracemalloc
import asyncio
import time
from typing import Union, List

from bottex2.platforms.py import PyMessage, PyReceiver
from bottex2 import aiotools

from testing.test_app import logic
from testing.test_app.main import bottex, setup_user_model


def rps(rpc, t):
    """repeats per second"""
    if t == 0:
        return float('inf')
    return 60 * rpc / t / 1000


async def bench(receiver: PyReceiver,
                cycles: int,
                repeats_per_cycle: Union[int, float] = 1E5):
    repeats_per_cycle = int(repeats_per_cycle)
    snapshots = []
    queue = asyncio.Queue()
    for i in range(cycles):
        message = PyMessage('message text', queue)
        start = time.time()
        for _ in range(repeats_per_cycle):
            receiver.recv_nowait(message)
            while not queue.empty():
                response = await queue.get()
                queue.task_done()
        total = time.time() - start
        print(rps(repeats_per_cycle, total))
        snap = tracemalloc.take_snapshot()
        snapshots.append(snap)

    # noinspection PyUnboundLocalVariable
    statistics(snapshots)


py_receiver = PyReceiver()
py_receiver.set_handler(logic.router)


def main(cycles, repeats):
    setup_user_model()
    tracemalloc.start()
    bottex.add_receiver(py_receiver)
    aiotools.run_async(
        bench(py_receiver, cycles, repeats),
        py_receiver.serve_async(),
    )


def statistics(snapshots: List[tracemalloc.Snapshot]):
    for prev_snap, snap in zip(snapshots, snapshots[1:]):
        stats = snap.compare_to(prev_snap, 'lineno')
        print()
        for stat in stats[:5]:
            print(stat)


if __name__ == '__main__':
    main(10, 1e5)
