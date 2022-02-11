"""Reload API."""

import argparse
import logging

from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Optional, Union, List

from reload.amazon import Amazon
from reload.configparser import parse_config, ReloadConfig
from reload.utils import flatten

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILE: PurePath = Path.cwd() / "reloads.yaml"
"""Default configuration file.

The default configuration file should be in the current working directory of the caller.
"""


# TODO: provide option to update zipapp so script updates when user runs it
# TODO: provide option to port/translate config file to latest version
def cli() -> object:
    """Create the command line interface."""

    parser = argparse.ArgumentParser(description='CLI for Reload, the ')
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="Enable verbosity/debug logging"
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="file",
        action="append",  # "extend" only in py3.8+
        nargs="+",
        type=str,
        help="Configuration file(s) to parse and run reloads from."
    )

    args = parser.parse_args()
    args.file = flatten(file)
    return args



class Reload:
    """Reload gift card balance based on configuration file."""

    _configs: List[ReloadConfig]
    """Card reload configurations."""


    def __init__(self, config_file: Optional[Union[str, PurePath]] = None) -> None:
        if config_file:
            self._configs = parse_config(config_file)
        else:
            logger.info(
                f"'config_file' was not defined, defaulting to '{DEFAULT_CONFIG_FILE}'"
            )
            if not DEFAULT_CONFIG_FILE.exists():
                raise FileNotFoundError(
                    f"Default config file not found in current working dir '{DEFAULT_CONFIG_FILE}'"
                )
            self._configs = parse_config(config_file)


#class Cache:


#if __name__ == "__main__":