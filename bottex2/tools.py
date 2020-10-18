import asyncio
import inspect


def merge_async_iterators(aiters):
    """
    https://stackoverflow.com/questions/55299564/join-multiple-async-generators-in-python
    """
    queue = asyncio.Queue(1)
    count = len(aiters)

    async def drain(aiter):
        nonlocal count
        async for item in aiter:
            await queue.put(item)
        count -= 1

    async def merged():
        while count:
            yield await queue.get()

    tasks = [asyncio.create_task(drain(aiter)) for aiter in aiters]
    return merged()


def merge_async_iterators2(aiters):
    """
    https://stackoverflow.com/questions/55299564/join-multiple-async-generators-in-python
    """
    queue = asyncio.Queue(1)
    run_count = len(aiters)
    cancelling = False

    async def iterate(aiter):
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

    async def merged(tasks):
        try:
            while run_count:
                raised, next_item = await queue.get()
                if raised:
                    cancel_tasks(tasks)
                    raise next_item
                yield next_item
        finally:
            cancel_tasks(tasks)

    def cancel_tasks(tasks):
        nonlocal cancelling
        cancelling = True
        for t in tasks:
            t.cancel()

    tasks_ = [asyncio.create_task(iterate(aiter)) for aiter in aiters]
    return merged(tasks_)


class MultiTask:
    def __init__(self):
        self._queue = asyncio.Queue()

    def add(self, task):
        self._queue.put_nowait(task)

    async def listen(self):
        task = await self._queue.get()
        await asyncio.gather(task, self.listen())


def have_kwargs_parameter(function):
    """Checks whenever the function accepts **kwargs parameter"""
    sig = inspect.signature(function)
    return any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
