import logging
from pathlib import Path
import time
from datetime import datetime

import discord

from src.yourmumbot.YourMumModel import YourMumModel
from helpers.logging import log_memory_used, reset_logging
import constants as cst


reset_logging()

# Args
log_level = logging.INFO

current_time = datetime.now().strftime('%H:%M:%S-%d-%m-%y')
filename = f"{cst.LOGS_DIR}/main/yourmumbot-{current_time}.log"
Path(filename).parent.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger(__name__)
logging.basicConfig(level=log_level, filename=filename)
logger.setLevel(log_level)


class YourMumClient(discord.Client):
    def __init__(self,
                 guild_id,
                 corrector="gingerit",
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.guild_id = int(guild_id)
        self.model = YourMumModel(corrector=corrector, logger=logger)
        self.corrector = corrector

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.model.__exit__(*args)

    @staticmethod
    def block(text, original):
        if text == "":
            return True
        if text.lower() == original.lower():
            return True
        if text.lower().strip() == 'your mum':
            return True
        if not 'your mum' in text.lower():
            return True
        return False

    async def on_ready(self):
        guild = self.get_guild(self.guild_id)
        print(
            f'{self.user} is connected to the following guild:\n'
            f'{guild.name} (id: {guild.id})\n'
            f'Running with corrector {self.corrector}'
        )
        print("Warming up the model...")
        self.model.warm_up()
        print("Ready!")

    async def on_message(self, message):
        if not message.author.bot:
            start = time.time()
            content = message.content
            yourmumify_content = " ".join(
                list(self.model.yourmumify(content)))
            # logger.info(log_memory_used())
            logger.info(f"Latency: {(time.time()-start):.4}s")
            if not self.block(yourmumify_content, content):
                await message.channel.send(
                    content=yourmumify_content,
                    reference=message,
                    mention_author=False)
