import logging
import os

import dotenv

dotenv.load_dotenv()

ENV = os.getenv("ENV", "DEV")
PROD = ENV == "PROD"

# api
API_PORT = os.environ["API_PORT"]
API_ENDPOINT = f"http://localhost:{API_PORT}/yourmumify"

# logs
LOG_FORMAT = "%(asctime)s::%(levelname)8s::%(name)s::%(request_id)5s:: %(message)s"
LOG_LEVEL = logging.INFO if PROD else logging.DEBUG

# your mum bot
BOT_TOKEN = os.environ[f"DISCORD_{'' if PROD else 'DEV_'}BOT_TOKEN"]
API_TIMEOUT = 10
