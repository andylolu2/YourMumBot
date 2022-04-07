import random
from datetime import datetime, timedelta

import discord
from discord.ext import commands


from bot.logger import logger, request_id
from bot.helper import post_api, block
from bot.contexts import mute_dict
from helper.timer import timer


class HelpCommand(commands.DefaultHelpCommand):
    def get_ending_note(self):
        return (
            "Apart from that, just say something and your mum will respond to it.\n"
            "For example, try 'A bot entered the chat.'"
        )


command_prefix = "mum "
client = commands.Bot(
    command_prefix=command_prefix,
    help_command=HelpCommand(no_category="Commands")
)


@client.command(name="stats")
async def stats(ctx: commands.Context):
    '''
    Your mum will tell you the current statistics
    '''
    num_servers = len(client.guilds)
    await ctx.send(f"Your mum is telling jokes in {num_servers} servers!")


@client.command(name="quiet!")
async def quiet(ctx: commands.Context):
    '''
    Your mum will shutup for a while
    '''
    cid = ctx.channel.id
    if cid in mute_dict and datetime.now() < mute_dict[cid]:
        return

    duration = random.uniform(15, 60)
    mute_dict[cid] = datetime.now() + timedelta(minutes=duration)
    await ctx.send(f"OK, fine. :triumph:")


@client.command(name="unmute")
async def unmute(ctx: commands.Context):
    '''
    Your mum will continue to annoy you
    '''
    cid = ctx.channel.id
    if cid in mute_dict:
        del mute_dict[cid]
    await ctx.message.add_reaction("🤫")


@client.listen()
async def on_ready():
    logger.info(f'{client.user} is connected to the following guilds:')
    for guild in client.guilds:
        logger.info(f'{guild.name} (id: {guild.id})')
    logger.info("Ready!")


@client.listen()
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    cid = message.channel.id
    if cid in mute_dict:
        if datetime.now() > mute_dict[cid]:
            del mute_dict[cid]
        else:
            return

    with timer(logger=logger, prefix="Total latency: "):
        request_id.set(request_id.get() + 1)

        content = str(message.clean_content)
        if content.startswith(command_prefix):
            return
        logger.debug(f"Input: {content}")

        yourmumify_content = await post_api(content)
        if not block(yourmumify_content, content):
            logger.debug(f"Yourmumified: {yourmumify_content}")
            await message.channel.send(
                content=yourmumify_content,
                reference=message,
                mention_author=False
            )
