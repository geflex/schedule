import asyncio
from functools import partial

import bottex
from bottex.drivers.drivers import Driver
from bottex.core.error_handling import on_error, err_safe_run


async def _create_coro(drivers):
    await asyncio.gather(*[d.run() if isinstance(d, Driver) else d() for d in drivers])


def _run(drivers):
    coro = _create_coro(drivers)
    loop = asyncio.get_event_loop()
    bottex.logger.info('Listening...')
    loop.run_until_complete(coro)


def run(drivers, restart_on_error=True, err_handler=on_error):
    # _init_app_modules()
    runner = partial(_run, drivers)
    if restart_on_error:
        err_safe_run(runner, err_handler)
    else:
        runner()
