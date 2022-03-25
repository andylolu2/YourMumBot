from typing import Optional
from contextlib import contextmanager
from logging import Logger
import time


@contextmanager
def timer(logger: Optional[Logger] = None, prefix: str = '', decimal: int = 2):
    start = time.time()
    yield
    time_spent = round(1000 * (time.time() - start), decimal)
    log_str = f"{prefix}{time_spent}ms"
    if logger is not None:
        logger.info(log_str)
    else:
        print(log_str)
