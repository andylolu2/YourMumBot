from helper.logger import get_logger
from api import LOG_FORMAT, LOG_NAME, LOG_LEVEL
from api.requestvars import g

logger = get_logger(
    name=LOG_NAME,
    log_format=LOG_FORMAT,
    level=LOG_LEVEL,
    callbacks=[
        ('client_ip', lambda: g().client_ip)
    ]
)
