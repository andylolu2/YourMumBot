import asyncio

request_id = 0
lock = asyncio.Lock()


def get_request_id():
    return request_id


async def inc_request_id():
    global request_id

    async with lock:
        request_id += 1
