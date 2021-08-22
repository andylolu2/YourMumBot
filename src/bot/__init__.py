import dotenv
import os
import logging

dotenv.load_dotenv()

ENV = os.getenv("ENV", "DEV")
assert ENV in ["DEV", "PROD"]
PROD = (ENV == "PROD")

# api
API_ENDPOINT = "http://localhost:80/yourmumify"

# logs
LOG_FORMAT = "%(asctime)s::%(levelname)8s::%(name)s::%(request_id)5s:: %(message)s"
LOG_LEVEL = logging.INFO

# your mum bot
BOT_TOKEN = os.getenv(f"DISCORD_{'' if PROD else 'DEV_'}BOT_TOKEN")
API_TIMEOUT = 10
