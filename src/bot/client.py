import discord
from discord.ext import commands

from bot.helper import block, post_api
from bot.logger import logger, request_id
from helper.timer import timer


class HelpCommand(commands.DefaultHelpCommand):
    def get_ending_note(self):
        return (
            "Apart from that, just say something and your mum will respond to it.\n"
            "For example, try '@Your Mum A bot entered the chat.'"
        )


client = commands.Bot(
    intents=discord.Intents.default(),
    command_prefix=commands.bot.when_mentioned,
    help_command=HelpCommand(no_category="Commands"),
)


@client.command(name="stats")
async def stats(ctx: commands.Context):
    """
    Your mum will tell you the current statistics
    """
    num_servers = len(client.guilds)
    await ctx.send(f"Your mum is telling jokes in {num_servers} servers!")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error


@client.listen()
async def on_ready():
    logger.info(f"{client.user} is connected to the following guilds:")
    for guild in client.guilds:
        logger.info(f"{guild.name} (id: {guild.id})")
    logger.info("Ready!")


@client.listen()
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    with timer(logger=logger, prefix="Total latency: "):
        prefix = f"@{client.user.name}"
        content = str(message.clean_content)

        if content.startswith(prefix):
            content = content[len(prefix) :]

        request_id.set(request_id.get() + 1)
        logger.debug(f"Input: {content}")

        yourmumify_content = await post_api(content)
        if not block(yourmumify_content, content):
            logger.debug(f"Yourmumified: {yourmumify_content}")
            await message.channel.send(
                content=yourmumify_content, reference=message, mention_author=False
            )
