"""Package utilities."""

import logging
import pickle
import shelve

from pathlib import PurePath
from typing import Union, Optional

logger = logging.getLogger(__name__)


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
    with shelve.open(state_file) as db:
        if state_name in db:
            obj = db[state_name]
        else:
            logger.info(
                f"Failed to fetch state. '{state_name}' does not exist in '{state_file}'"
                " database."
            )
            obj = None

    return obj


def save_state(obj: object, state_name: str, state_file: Union[str, PurePath]) -> None:
    logger.info(f"Saving state of '{state_name}' to '{state_file}' database.")
    with shelve.open(state_file) as db:
        db[state_name] = obj
