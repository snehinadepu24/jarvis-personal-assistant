# Central logging configuration for the Jarvis project

"""
This module sets up a consistent logging system that writes to rotating
log files and also streams INFO+ messages to the console.

Two files are created under the project ``logs`` directory:
* ``backend_debug.log`` – DEBUG and higher (full trace)
* ``backend_error.log`` – ERROR and higher (quick error view)

Call ``configure_logging()`` as early as possible (e.g. at the top of
``backend/server.py``) before any other modules import ``logging``.
"""

import logging
import logging.handlers
import os
from pathlib import Path

# Directory that will contain the log files (project root / logs)
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def configure_logging() -> None:
    """Configure the root logger with rotating file handlers.

    This function is idempotent – calling it multiple times will replace any
    existing handlers with the same configuration, ensuring a clean state.
    """
    # Ensure the logs directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------------
    # Formatters
    # --------------------------------------------------------------
    detailed_fmt = (
        "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
    )
    simple_fmt = "%(asctime)s | %(levelname)-8s | %(message)s"

    detailed_formatter = logging.Formatter(detailed_fmt, "%Y-%m-%d %H:%M:%S")
    simple_formatter = logging.Formatter(simple_fmt, "%Y-%m-%d %H:%M:%S")

    # --------------------------------------------------------------
    # Handlers
    # --------------------------------------------------------------
    debug_file = logging.handlers.RotatingFileHandler(
        LOG_DIR / "backend_debug.log",
        maxBytes=5 * 1024 * 1024,  # 5 MiB per file
        backupCount=5,
        encoding="utf-8",
    )
    debug_file.setLevel(logging.DEBUG)
    debug_file.setFormatter(detailed_formatter)

    error_file = logging.handlers.RotatingFileHandler(
        LOG_DIR / "backend_error.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_file.setLevel(logging.ERROR)
    error_file.setFormatter(detailed_formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)  # console shows INFO+ by default
    console.setFormatter(simple_formatter)

    # --------------------------------------------------------------
    # Root logger configuration
    # --------------------------------------------------------------
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    # Clear any existing handlers (the default StreamHandler from the stdlib)
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(debug_file)
    root.addHandler(error_file)
    root.addHandler(console)

    # Reduce noise from very chatty third‑party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    root.debug("Logging configuration loaded – files in %s", LOG_DIR)

# When executed directly, set up logging and emit a test line
if __name__ == "__main__":
    configure_logging()
    logging.getLogger(__name__).info("Logging test – configuration active")

