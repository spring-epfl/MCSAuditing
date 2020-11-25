"""
Logging functionalities.
"""

import logging

LOGGER_NAME = "mcs-auditing"

def setup_logger() -> logging.Logger:
    """
    Setup the logger.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


LOGGER: logging.Logger = setup_logger()
