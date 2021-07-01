import os

from dotenv import load_dotenv

# from src.oocbot.OutOfConClient import OutOfConClient
from src.yourmumbot.YourMumClient import YourMumClient
import constants as cst

load_dotenv()

with YourMumClient(corrector="language_tools") as client:
    client.run(cst.BOT_TOKEN)
