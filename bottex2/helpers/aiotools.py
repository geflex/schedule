import asyncio
from typing import Collection, AsyncIterator, Awaitable, Iterable


def merge_async_iterators(aiters: Collection[AsyncIterator]):
    """
    https://stackoverflow.com/questions/55299564/join-multiple-async-generators-in-python
    """
    queue = asyncio.Queue(1)
    run_count = len(aiters)
    cancelling = False

    async def iterate(aiter: AsyncIterator):
        nonlocal run_count
        try:
            async for item in aiter:
                await queue.put((False, item))
        except Exception as e:
            if not cancelling:
                await queue.put((True, e))
            else:
                raise
        finally:
            run_count -= 1

    async def merged(tasks: Iterable[asyncio.Task]):
        try:
            while run_count:
                raised, next_item = await queue.get()
                if raised:
                    cancel_tasks(tasks)
                    raise next_item
                yield next_item
        finally:
            cancel_tasks(tasks)

    def cancel_tasks(tasks: Iterable[asyncio.Task]):
        nonlocal cancelling
        cancelling = True
        for t in tasks:
            t.cancel()

    tasks_ = [create_task(iterate(aiter)) for aiter in aiters]
    return merged(tasks_)


def raise_exc_callback(task: asyncio.Task):
    exc = task.exception()
    if exc:
        # !!! Fix this
        cancel_pending_tasks()
        asyncio.get_event_loop().stop()
        raise exc


def create_task(coro: Awaitable, *, name=None, done_callback=raise_exc_callback):
    task = asyncio.create_task(coro, name=name)
    if done_callback is not None:
        task.add_done_callback(done_callback)
    return task


def run_pending_tasks(loop: asyncio.AbstractEventLoop):
    pending = asyncio.all_tasks()
    loop.run_until_complete(asyncio.gather(*pending))


def cancel_pending_tasks():
    tasks = asyncio.all_tasks()
    for task in tasks:
        task.cancel()


def run_async(*coros: Awaitable, debug=False):
    loop = asyncio.get_event_loop()
    loop.set_debug(debug)
    loop.run_until_complete(asyncio.gather(*coros))
