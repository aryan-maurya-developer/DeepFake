"""Shared logging helpers."""

from __future__ import annotations

import logging
import sys

from settings import settings


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s [%(filename)s:%(lineno)d] - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
