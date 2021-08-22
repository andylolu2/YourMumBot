import logging

# corenlp
CORENLP_ENDPOINT = "http://localhost:9000"
CORENLP_TIMEOUT = 30000  # in ms

# language tools
LANG_NAME = "en-US"
LT_ENDPOINT = "http://localhost:8010"
LT_MAX_RETRIES = 10
LT_TIMEOUT = 3  # in s

# sanitize input
INPUT_MAX_WORDS = 25
INPUT_MAX_CHAR = 150

# model
MAX_SUB_SAMPLES = 5
WARM_UP_TEXT = "warm the model up"
STAY_WARM_PERIOD = 60

# logger config
LOG_NAME = "yourmum.api"
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s::%(levelname)8s::%(name)s::%(client_ip)s:: %(message)s"
LOG_EVERY = 10
