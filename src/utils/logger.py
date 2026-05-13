from __future__ import annotations

import logging

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("insurance_analysis")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.addHandler(console_handler)
    logger.propagate = False
    return logger


__all__ = ["setup_logger"]
