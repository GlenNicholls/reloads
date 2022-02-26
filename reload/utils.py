"""Package utilities."""

import logging
import pickle
import shelve
import sys

from logging.handlers import RotatingFileHandler
from pathlib import PurePath, Path
from typing import Union, Optional

from rich.logging import RichHandler


logger = logging.getLogger(__name__)


def config_logger(
    filename: Optional[Union[str, PurePath]] = None,
    level: int = logging.INFO,
    fmt: str = "%(asctime)s %(levelname)-s - %(message)s",
    datefmt: str = "[%X]",
    file_mode: str = "a",
    file_level: int = logging.DEBUG,
    file_format: str = "[%(asctime)s] %(levelname)-8s - %(message)s     (%(pathname)s:%(lineno)s)",
    file_datefmt: str = "%Y-%m-%d %H:%M:%S",
    enable_rich: bool = True,
) -> None:
    """Configure terminal and file loggers.

    .. note::
        A console/terminal logger will always be created.

    .. note::
        This uses :class:`logging.handlers.RotatingFileHandler` with a limit of 0.5 MB
        for the log file if enabled. It also retains a backup of 5 log files.

    Args:
        filename:
            Log file, set to ``None`` for no log file.
        level:
            Terminal log level like ``logging.INFO`` or the ``int`` equivalent.
            Reference `Logging Levels
            <https://docs.python.org/3/library/logging.html#logging-levels>`_.
        fmt:
            Terminal log format (only if ``enable_rich=False``). For example,
            ``[%(asctime)s] %(levelname)-s - %(message)s`` would produce a message like
            ``[14:21:36] INFO - some info`` if ``datefmt='[%X]'``. Reference
            `LogRecord Attributes
            <https://docs.python.org/3/library/logging.html#logrecord-attributes>`_.
        datefmt:
            Terminal log date format, only applicable if ``fmt`` includes a LogRecord
            date attribute. Reference `logging.Formatter.formatTime
            <https://docs.python.org/3/library/logging.html#logging.Formatter.formatTime>`_.
        file_mode:
            File handler file mode
        file_level:
            File handler log level
        file_format:
            File handler logging
        file_datefmt:
            Date format for file handler
        enable_rich:
            True if :class:`rich.logging.RichHandler` should be used to make console
            logs colorful/pretty. When true, ``fmt`` will be set to ``%(message)s``.
    """
    # get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # configure console handler
    if enable_rich:
        ch = RichHandler(
            show_time=True,
            show_path=level <= logging.DEBUG,
            log_time_format=datefmt,
        )
    else:
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    ch.name = "console_handler"
    ch.setLevel(level)
    root_logger.addHandler(ch)

    # configure file handler
    if filename:
        filename = Path(filename).resolve()
        if not filename.parent.exists():
            logger.info(f"{filename.parent} does not exist, creating")
            filename.parent.mkdir(parents=True)
        fh = RotatingFileHandler(
            filename,
            mode=file_mode,
            maxBytes=0.5e6,
            backupCount=5
        )
        fh.name = "file_handler"
        fh.setLevel(file_level)
        fh.setFormatter(logging.Formatter(fmt=file_format, datefmt=file_datefmt))
        root_logger.addHandler(fh)

        # log information and create break in log file that makes it easier to find a
        # specific session when append is used
        logger.debug("="*50)
        logger.debug(f"Log session starts")
        logger.info(f"Logs will be saved to '{filename}'")
        logger.debug("="*50)


def flatten(nested_list: list) -> list:
    """Flatten nested list of any dimension to single dimension.

    Args:
        Nested_list: list or list of lists of any dimension/depth

    Returns:
        Flattened ``nested_list``.

    >>> a = [1, [2, 3], [[[4, "a"]]]]
    >>> flatten(a)
    [1,2,3,4,"a"]
    """
    if len(nested_list) == 0:
        return nested_list
    if isinstance(nested_list[0], list):
        return flatten(nested_list[0]) + flatten(nested_list[1:])
    return nested_list[:1] + flatten(nested_list[1:])


def load_state(state_name: str, state_file: Union[str, PurePath]) -> Optional[object]:
    logger.debug(f"Fetching state of '{state_name}' from '{state_file}' database.")
    if not Path(state_file).exists():
        logger.debug(f"State file does not exist yet '{state_file}'")
        return None

    with shelve.open(str(state_file)) as db:
        if state_name in db:
            return db[state_name]
        else:
            logger.info(
                f"Failed to fetch state. '{state_name}' does not exist in '{state_file}'"
                " database."
            )
            return None


def save_state(obj: object, state_name: str, state_file: Union[str, PurePath]) -> None:
    logger.info(f"Saving state of '{state_name}' to '{state_file}' database.")
    with shelve.open(str(state_file)) as db:
        db[state_name] = obj
