import logging
import guppy


def reset_logging():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


def memory_used(unit: str = 'm') -> int:
    unit = unit.lower()
    offset = 1
    if unit.startswith('g'):  # in gigabytes
        offset = 1e-9
    elif unit.startswith('m'):  # in megabytes
        offset = 1e-6
    elif unit.startswith('k'):  # in kilobytes
        offset = 1e-3

    return int(guppy.hpy().heap().size * offset)


def log_memory_used(unit: str = 'm') -> str:
    return f"Memory used: {memory_used(unit=unit)} MB"
