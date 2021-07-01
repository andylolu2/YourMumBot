import heapq

import discord

from src.oocbot.OutOfConModel import OutOfConModel


class OutOfConClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = OutOfConModel()

    async def on_ready(self):
        print(f'{self.user} is connected to the following guilds:')
        for guild in self.guilds:
            print(f'{guild.name} (id: {guild.id})')

    async def on_message(self, message):
        if not message.author.bot:
            content = message.content
            toxic_substrings = self.model.get_toxic_sublists(
                content, key="toxicity", threshhold=0)
            if len(toxic_substrings) > 0:
                top_k = heapq.nlargest(5, toxic_substrings, lambda t: t[0])
                await message.channel.send(
                    content=str(top_k),
                    reference=message,
                    mention_author=False)
