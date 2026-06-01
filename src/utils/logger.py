import logging
from pathlib import Path
from datetime import datetime

# Global variable to store the log file path for the current run
_LOG_FILE = None
_LOG_FILE_FAILED = False


def get_logger(name: str):
    global _LOG_FILE, _LOG_FILE_FAILED

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    # On Streamlit Cloud the file system may be read-only or the path may not
    # resolve.  Create a file handler only once, and fall back to a stream
    # (console) handler on failure so the app never crashes at import time.
    if _LOG_FILE is None and not _LOG_FILE_FAILED:
        try:
            date_dir = datetime.now().strftime("%Y-%m-%d")
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            # Resolve relative to *this* file so it works regardless of CWD
            project_root = Path(__file__).resolve().parents[2]
            log_dir = project_root / "logs" / date_dir
            log_dir.mkdir(parents=True, exist_ok=True)
            _LOG_FILE = log_dir / f"{timestamp}.log"
        except OSError:
            _LOG_FILE_FAILED = True

    if _LOG_FILE is not None and not _LOG_FILE_FAILED:
        try:
            handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
            formatter = logging.Formatter(
                "[%(asctime)s]: %(filename)s - Line %(lineno)d: %(levelname)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.propagate = False
            return logger
        except OSError:
            _LOG_FILE_FAILED = True

    # Fallback: console / stream handler (always works)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s]: %(filename)s - Line %(lineno)d: %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    return logger
