from pathlib import Path

# paths
PROJECT_ROOT = str(Path(__file__).resolve().parent)
CORENLP_HOME = PROJECT_ROOT + "/lib/stanford-corenlp/stanford-corenlp-4.2.2"
LOGS_DIR = PROJECT_ROOT + "/logs/"

# your mum bot
LOG_EVERY = 10

# corenlp
CORENLP_TIMEOUT = 3000
CORENLP_ENDPOINT = "http://localhost:5000"
CORENLP_MEMORY = "1G"
CORENLP_THREADS = 1

# tests
TESTING_SAMPLES = 50
