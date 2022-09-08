from bot import LOG_FORMAT, LOG_LEVEL
from bot.contexts import get_request_id
from helper.logger import get_logger

logger = get_logger(
    name=__name__,
    log_format=LOG_FORMAT,
    level=LOG_LEVEL,
    callbacks=[("request_id", get_request_id)],
)
