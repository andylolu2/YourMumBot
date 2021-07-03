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
MAX_CONNECTIONS = 2
INPUT_MAX_WORDS = 35
INPUT_MAX_CHAR = 250
LOG_EVERY = 10

# corenlp
CORENLP_TIMEOUT = 3000
CORENLP_ENDPOINT = "http://localhost:5000"
CORENLP_MEMORY = "200M" if PROD else "2G"
CORENLP_THREADS = 1 if PROD else 4

# tests
TESTING_SAMPLES = 50
