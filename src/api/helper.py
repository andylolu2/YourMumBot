from typing import Callable, Optional, Awaitable
from functools import wraps
import traceback
import asyncio

from fastapi.concurrency import run_in_threadpool

from api.logger import logger

# Ref: https://gist.github.com/Razkaroth/8f784f196fde94a580474f048333db6a


def repeat_every(*, seconds: float, wait_first: bool = False):
    def decorator(func: Callable[[], Optional[Awaitable[None]]]):
        is_coroutine = asyncio.iscoroutinefunction(func)

        @wraps(func)
        async def wrapped():
            async def loop():
                if wait_first:
                    await asyncio.sleep(seconds)
                while True:
                    try:
                        if is_coroutine:
                            await func()
                        else:
                            await run_in_threadpool(func)
                    except Exception as e:
                        logger.error(str(e))
                    await asyncio.sleep(seconds)

            asyncio.create_task(loop())

        return wrapped

    return decorator
