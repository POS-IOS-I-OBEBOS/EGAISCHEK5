"""Utilities for configuring application logging."""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

_DEFAULT_LOG_FILENAME = "barcode_reader.log"


def configure_logging(log_path: Optional[Path] = None, *, level: int = logging.DEBUG) -> Path:
    """Configure logging for the application and return the log file path."""
    if log_path is None:
        log_path = Path.cwd() / _DEFAULT_LOG_FILENAME
    else:
        log_path = Path(log_path)

    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(level)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(logging.INFO)

    handlers = [file_handler, stream_handler]

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )

    logging.getLogger(__name__).debug("Logging configured. Writing to %s", log_path)
    return log_path
