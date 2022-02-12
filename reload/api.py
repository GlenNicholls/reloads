"""Reload API."""

import argparse
import logging
import random

import reload

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePath
from typing import Optional, Union, List, Tuple

from reload.amazon import Amazon
from reload.configparser import parse_config, ReloadConfig
from reload.utils import flatten, save_state, load_state

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILE: PurePath = Path.cwd() / "reloads.yaml"
"""Default configuration file.

The default configuration file should be in the current working directory of the caller.
"""

_STATE_FILE: PurePath = Path.cwd() / ".cache/state.db"
"""Cache directory for saving/loading state."""


# TODO: provide option to update zipapp so script updates when user runs it
# TODO: provide option to port/translate config file to latest version
def cli() -> object:
    """Create the command line interface."""

    parser = argparse.ArgumentParser(description=reload.__doc__)
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
    parser.add_argument(
        "-p",
        "--prompt",
        dest="prompt",
        action="store_true",
        default=False,
        help="Always prompt the user to continue before clicking anything."
    )

    args = parser.parse_args()
    args.file = flatten(args.file)

    return args


@dataclass
class ReloadState:
    config: ReloadConfig

    num_complete: int = 0
    """Number of purchases completed for the current month."""

    #last_purchase_date: Optional[datetime] = None
    #"""Last purchase date and time.
#
    #This is used when loading the object such that the runner can keep track of when to
    #reset the number of completed purchases.
    #"""

    next_purchase_date: Optional[datetime] = None
    """When the next purchase should be completed."""

    purchase_info: Optional[dict] = None


class Reload:
    """Reload gift card balance based on configuration file."""

    _configs: List[ReloadConfig]
    """Card reload configurations."""


    def __init__(self, config_file: Optional[Union[str, PurePath]] = None, state_file: Optional[Union[str, PurePath]] = None) -> None:
        if config_file is None:
            logger.info(
                f"'config_file' was not defined, defaulting to '{DEFAULT_CONFIG_FILE}'"
            )
            if not DEFAULT_CONFIG_FILE.exists():
                raise FileNotFoundError(
                    f"Default config file not found in current working dir '{DEFAULT_CONFIG_FILE}'"
                )
            config_file = DEFAULT_CONFIG_FILE

        self._configs = parse_config(config_file)
        self._db_file = state_file if state_file else _STATE_FILE


    def get_state(self, cfg: ReloadConfig) -> ReloadState:
        # Attempt to load state if it already exists
        state = load_state(cfg.name, self._db_file)
        if state is None:
            # State does not exist so create it.
            state = ReloadState(config=cfg)
        elif state.config != cfg:
            # If the configuration has changed, reset the state config
            if state.config.card == cfg.card:
                # Config changed but card did not, so the completed purchases is
                # still valid.
                logger.info(
                    f"Config does not match database state for '{cfg.name}'."
                    " Resetting cache of config but keeping the completed purchases."
                )
                state.config = cfg
            else:
                # The card changed so we have to reset the state.
                logger.info(
                    f"Config does not match database state for '{cfg.name}'. The"
                    " card changed so the whole cache will be reset."
                )
                state = ReloadState(config=cfg)

        # If the next purchase date isn't set, set it to now so it will get run
        if state.next_purchase_date is None:
            state.next_purchase_date = datetime.now()

        # Configure the purchase information if it isn't set

        return state


    def purchase(config: ReloadConfig) -> None:
        # Open browser and log in
        amzn = Amazon(
            username=config.username,
            password=config.password,
            card=config.card
        )

        # Determine an amount to spend and round to 2 decimal places
        amount = random.uniform(config.amounts[0], config.amounts[1])
        amount = round(amount, 2)

        amzn.reload_balance(amount)


    def run(self):
        for config in self._configs:
            # Get the state of this config from the database/cache
            state = self.get_state(config)

            # Run purchase logic
            if state.config.days[0] <= datetime.now().day <= state.config.days[1]:
                self.purchase(state.config)
