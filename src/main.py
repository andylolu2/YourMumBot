import os

from dotenv import load_dotenv

# from src.oocbot.OutOfConClient import OutOfConClient
from src.yourmumbot.YourMumClient import YourMumClient

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD_ID = os.getenv('DISCORD_GUILD_ID')

with YourMumClient(guild_id=GUILD_ID, corrector="language_tools") as client:
    client.run(TOKEN)
