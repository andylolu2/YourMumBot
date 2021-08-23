import logging

from helper.logger import get_logger
from api import LOG_FORMAT, LOG_NAME, LOG_LEVEL
from api.requestvars import g

logging.getLogger().handlers.clear()
uvi_error = logging.getLogger("uvicorn.error")
uvi_access = logging.getLogger("uvicorn.access")
uvi_error.handlers.clear()
uvi_access.handlers.clear()
uvi_error.propagate = False
uvi_access.propagate = False

logger = get_logger(
    name=LOG_NAME,
    log_format=LOG_FORMAT,
    level=LOG_LEVEL,
    callbacks=[
        ('client_ip', lambda: g().client_ip)
    ]
)
