from typing import Optional
from contextvars import ContextVar
import asyncio
import time

import aiohttp
import aiohttp
import discord

from bot import API_ENDPOINT, API_TIMEOUT, LOG_FORMAT, LOG_LEVEL
from helper.logger import get_logger


class YourMumClient(discord.Client):
    req_counter = 0
    request_id = ContextVar('request_id')
    logger = get_logger(
        name=__name__,
        log_format=LOG_FORMAT,
        level=LOG_LEVEL,
        contextvars=[('request_id', request_id)]
    )

    async def post_api(self, text: str) -> Optional[str]:
        body = {'msg': text}
        try:
            start = time.time()
            timeout = aiohttp.ClientTimeout(total=API_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(API_ENDPOINT, json=body) as r:
                    self.logger.info(f"API latency: {(time.time()-start):.4}s")
                    if r.status == 200:
                        res = await r.json()
                        res = " ".join(res['response'])
                        return res
                    else:
                        self.logger.warning(
                            f'API respond with code {r.status}.')
                        return None
        except asyncio.TimeoutError:
            self.logger.warning(f'API did not respond in {API_TIMEOUT}s.')
            return None

    @staticmethod
    def block(text, original):
        if not isinstance(text, str):
            return True
        yourmum = "your mum"
        _text = text.lower().replace(" ", "")
        _yourmum = yourmum.lower().replace(" ", "")
        _original = original.lower().replace(" ", "")
        if text == "":
            return True
        if _text == _original:
            return True
        if _text == _yourmum:
            return True
        # sanity check
        if not 'your mum' in text.lower():
            return True
        return False

    async def on_ready(self):
        self.logger.info(f'{self.user} is connected to the following guilds:')
        for guild in self.guilds:
            self.logger.info(f'{guild.name} (id: {guild.id})')
        self.logger.info("Warming up the model...")
        self.logger.info("Ready!")

    async def on_message(self, message: discord.Message):
        if not message.author.bot:
            # time inference latency
            start = time.time()
            current_id = self.req_counter
            self.req_counter += 1
            self.request_id.set(current_id)

            content = message.clean_content
            self.logger.info(f"Input: {content}")

            yourmumify_content = await self.post_api(content)
            if not self.block(yourmumify_content, content):
                self.logger.info(f"Yourmumified: {yourmumify_content}")
                await message.channel.send(
                    content=yourmumify_content,
                    reference=message,
                    mention_author=False)
            self.logger.info(f"Total latency: {(time.time()-start):.4}s")
