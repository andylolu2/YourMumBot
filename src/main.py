import os

from dotenv import load_dotenv

# from src.oocbot.OutOfConClient import OutOfConClient
from src.yourmumbot.YourMumClient import YourMumClient

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

with YourMumClient(corrector="language_tools") as client:
    client.run(TOKEN)
