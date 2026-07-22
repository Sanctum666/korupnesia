import sys
from pathlib import Path

from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

_configured = False


def _has_component(record):
    return "component" in record["extra"]


def _stderr_format(record):
    if _has_component(record):
        return "<level>[{level}]</level>: <green>{time}</green> [{extra[component]}] | {message}\n"
    return "<level>[{level}]</level>: <green>{time}</green> | {message}\n"


def _file_format(record):
    if _has_component(record):
        return "[{level}] {time:YYYY-MM-DD HH:mm:ss.SSS ZZ} [{extra[component]}] | {name}:{function}:{line} | {message}:{extra}\n"
    return "[{level}] {time:YYYY-MM-DD HH:mm:ss.SSS ZZ} | {name}:{function}:{line} | {message}:{extra}\n"


def setup_logger(*, level: str = "INFO"):
    global _configured

    if _configured:
        return

    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()

    logger.add(
        sys.stderr,
        level=level,
        enqueue=True,
        format=_stderr_format,
    )

    logger.add(
        log_dir / "app.log",
        level=level,
        rotation="100 MB",
        retention="30 days",
        compression="gz",
        encoding="utf-8",
        enqueue=True,
        backtrace=True,
        format=_file_format,
    )

    _configured = True


setup_logger()
