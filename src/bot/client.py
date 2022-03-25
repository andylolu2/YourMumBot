from typing import Optional
from contextvars import ContextVar
import asyncio

from aiohttp import ClientSession, ClientTimeout
import discord

from bot import API_ENDPOINT, API_TIMEOUT, LOG_FORMAT, LOG_LEVEL
from helper.logger import get_logger
from helper.timer import timer


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
        with timer(logger=self.logger, prefix="API latency: "):
            try:
                async with ClientSession(timeout=ClientTimeout(API_TIMEOUT)) as session:
                    async with session.post(API_ENDPOINT, json=body) as r:
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
        if message.author.bot:
            return

        with timer(logger=self.logger, prefix="Total latency: "):
            current_id = self.req_counter
            self.req_counter += 1
            self.request_id.set(current_id)

            content = message.clean_content
            self.logger.debug(f"Input: {content}")

            yourmumify_content = await self.post_api(content)
            if not self.block(yourmumify_content, content):
                self.logger.debug(f"Yourmumified: {yourmumify_content}")
                await message.channel.send(
                    content=yourmumify_content,
                    reference=message,
                    mention_author=False)
