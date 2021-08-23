from typing import Tuple, Callable, Any, List
from contextvars import ContextVar
import logging


class ContextFilter(logging.Filter):
    def __init__(self,
                 contextvar_name: str,
                 contextvar: ContextVar,
                 name: str = '') -> None:
        super().__init__(name=name)
        self.contextvar_name = contextvar_name
        self.contextvar = contextvar

    def filter(self, record: logging.LogRecord):
        try:
            value = self.contextvar.get()
        except LookupError:
            value = ''
        setattr(record, self.contextvar_name, value)
        return super().filter(record)


class CallBackFilter(logging.Filter):
    def __init__(self,
                 contextvar_name: str,
                 callback: Callable[[], Any],
                 name: str = '') -> None:
        self.contextvar_name = contextvar_name
        self.callback = callback
        super().__init__(name=name)

    def filter(self, record: logging.LogRecord):
        try:
            value = self.callback()
        except Exception:
            value = ''
        setattr(record, self.contextvar_name, value)
        return super().filter(record)


def get_logger(name: str,
               log_format: str,
               level: int,
               contextvars: List[Tuple[str, ContextVar]] = [],
               callbacks: List[Tuple[str, Callable[[], Any]]] = []
               ) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()

    # log format
    formatter = logging.Formatter(log_format)

    # stdout handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # set level to all
    logger.setLevel(logging.DEBUG)

    # add custom contextvars that can be used in log_format
    for var_name, var in contextvars:
        f = ContextFilter(var_name, var)
        logger.addFilter(f)

    # add custom callbacks
    for var_name, cb in callbacks:
        f = CallBackFilter(var_name, cb)
        logger.addFilter(f)

    return logger
