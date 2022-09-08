import asyncio
from typing import Optional

from aiohttp import ClientSession, ClientTimeout

from bot import API_ENDPOINT, API_TIMEOUT
from bot.logger import logger
from helper.timer import timer


async def post_api(text: str) -> Optional[str]:
    body = {"msg": text}
    with timer(logger=logger, prefix="API latency: "):
        try:
            async with ClientSession(timeout=ClientTimeout(API_TIMEOUT)) as session:
                async with session.post(API_ENDPOINT, json=body) as r:
                    if r.status == 200:
                        res = await r.json()
                        res = " ".join(res["response"])
                        return res
                    else:
                        logger.warning(f"API respond with code {r.status}.")
                        return None
        except asyncio.TimeoutError:
            logger.warning(f"API did not respond in {API_TIMEOUT}s.")
            return None


def block_input(text: str):
    _text = text.lower().replace(" ", "")
    return len(_text) == 0


def block_output(text, original):
    if not isinstance(text, str):
        return True
    _text = text.lower().replace(" ", "")
    if _text in {"", "yourmum"}:
        return True
    _original = original.lower().replace(" ", "")
    if _text == _original:
        return True
    # sanity check
    if not "your mum" in text.lower():
        return True
    return False
