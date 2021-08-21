from pathlib import Path
import dotenv
import os

dotenv.load_dotenv()

ENV = os.environ.get("ENV", "DEV")
assert ENV in ["DEV", "PROD"]
PROD = (ENV == "PROD")

# paths
PROJECT_ROOT = str(Path(__file__).resolve().parent)
CORENLP_HOME = PROJECT_ROOT + "/lib/stanford-corenlp/stanford-corenlp-4.2.2"
LOGS_DIR = PROJECT_ROOT + "/logs/"

# your mum bot
BOT_TOKEN = os.getenv(f"DISCORD_{'' if PROD else 'DEV_'}BOT_TOKEN")
MAX_CONNECTIONS = 1
LOG_EVERY = 10
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s: %(message)s"
WARM_UP_TEXT = "warm the model up"
STAY_WARM_PERIOD = 60

# tests
TESTING_SAMPLES = 50
