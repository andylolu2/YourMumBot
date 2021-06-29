import time
from datetime import datetime
import logging
from pathlib import Path

import numpy as np

import constants as cst
from helpers.logging import reset_logging, log_memory_used
from data.processed.DiscordChat import DiscordChat
from src.yourmumbot.YourMumModel import YourMumModel

reset_logging()  # fix bug in stanza

# Args
log_level = logging.INFO
total = cst.TESTING_SAMPLES

# setup logging
current_time = datetime.now().strftime('%H:%M:%S-%d-%m-%y')
filename = f"{cst.LOGS_DIR}/tests/yourmumbot-{current_time}.log"
Path(filename).parent.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger('tester')
logging.basicConfig(level=log_level, filename=filename)
logger.setLevel(log_level)

with YourMumModel(corrector="language_tools", logger=logger) as model:
    # setup
    chat = DiscordChat()
    times = []

    # warmup
    model.warm_up()
    logger.info(log_memory_used())

    # logs
    tmp = f"Benchmarking on {total} samples..."
    logger.info(tmp)
    print(tmp)

    # main loop
    for msg in chat.sample(total):
        start_time = time.time()
        outputs = model.yourmumify(msg)
        output = " ".join(outputs)
        if output != "":
            logger.info(f"Input:  {msg}")
            logger.info(f"Output: {output}\n")
        times.append(time.time() - start_time)

    # logs
    tmp = log_memory_used()
    print(tmp)
    logger.info(tmp)

    tmp = f"Average inference time: {np.mean(times):.4}+-{np.std(times):.2}s / sample"
    print(tmp)
    logger.info(tmp)
