"""Reload API."""

import argparse
import logging
import random
import time

import reload

from dataclasses import dataclass
from datetime import datetime, timedelta
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

DEFAULT_LOG_FILE: PurePath = Path.cwd() / "reloads.log"
"""Default log file.

The default log file should be in the current working directory of the caller.
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
        type=str,
        default=str(DEFAULT_CONFIG_FILE),
        help=(
            "YAML configuration file to parse and run reloads from. Defaults to"
            " ``<CWD>/reloads.yaml``"
        )
    )
    parser.add_argument(
        "-l",
        "--log-file",
        dest="log_file",
        type=str,
        default=str(DEFAULT_LOG_FILE),
        help=(
            "Log file to save logs to. Defaults to  ``<CWD>/reloads.log``. The log file"
            " will be rotated after it reaches a certain size and 5 backups will be"
            " maintained."
        )
    )
    #parser.add_argument(
    #    "-p",
    #    "--prompt",
    #    dest="prompt",
    #    action="store_true",
    #    default=False,
    #    help="Prompt the user to continue before submitting purchase."
    #)

    return parser


@dataclass
class PurchaseInfo:
    date: datetime
    """Date of the purchase execution.

    This is the date the purchase function was called. Reference
    :data:`~reload.api.PurchaseInfo.purchased` to determine if the purchase went through.
    """

    amount: float
    """Amount of the purchase."""

    num_complete_for_month: int
    """Number of purchases complete for the month."""

    purchased: bool
    """Purchase was executed.

    If there was an error with the purchase, this will be false to state that the
    purchase did not go through.
    """

    #errors: List[str]
    #"""Errors encountered during purchase."""


# TODO: write method to dump state to YAML file for debugging
@dataclass
class ReloadState:
    config: ReloadConfig

    num_complete: int = 0
    """Number of purchases completed for the current month."""

    next_purchase_date: Optional[datetime] = None
    """When the next purchase should be completed."""

    purchases: Optional[List[PurchaseInfo]] = None


class Reload:
    """Reload gift card balance based on configuration file."""


    def __init__(self, config_file: Union[str, PurePath], state_file: Optional[Union[str, PurePath]] = None) -> None:
        config_file = Path(config_file)
        if not config_file.exists():
            raise FileNotFoundError(
                f"Config file does not exist ({config_file}). You must either specify"
                " the config file or create one in the current working directory"
                f" matching the name '{DEFAULT_CONFIG_FILE}'."
            )

        self._configs: List[ReloadConfig] = parse_config(config_file)
        self._db_file = state_file if state_file else _STATE_FILE


    def get_state(self, config: ReloadConfig) -> ReloadState:
        # Attempt to load state if it already exists
        state = load_state(config.name, self._db_file)

        if state is None:
            # State does not exist so create it.
            state = ReloadState(config=config)
        elif state.config != config:
            # If the configuration has changed, reset the state config
            if state.config.card == config.card:
                # Config changed but card did not, so the completed purchases is
                # still valid.
                logger.info(
                    f"Config does not match database state for '{config.name}'."
                    " Resetting cache of config but keeping the completed purchases."
                )
                state.config = config
            else:
                # The card changed so we have to reset the state.
                logger.info(
                    f"Config does not match database state for '{config.name}'. The"
                    " card changed so the whole cache will be reset."
                )
                state = ReloadState(config=config)

        # If the next purchase date isn't set, set it to now so it will get run
        if state.next_purchase_date is None:
            state.next_purchase_date = datetime.now()

        # Configure the purchase information if it isn't set

        return state


    def run_purchases(self, state: ReloadState) -> ReloadState:
        now = datetime.now()
        cfg = state.config
        min_day, max_day = cfg.days
        amzn = Amazon(
            username=cfg.username,
            password=cfg.password,
            card=cfg.card
        )

        # run reloads and wait a random amount of time between each purchase
        num_reloads = cfg.rand_burst(state.num_complete) if cfg.burst else 1
        for _ in range(num_reloads):
            amount = cfg.rand_amount()
            ok = amzn.reload_balance(amount)

            if ok:
                state.num_complete += 1
            else:
                logger.error("Error while reloading balance")

            # Keep track of purchase information.
            purch_info = PurchaseInfo(
                date=datetime.now(),
                amount=amount,
                num_complete_for_month=state.num_complete,
                purchased=ok
            )
            if state.purchases is None:
                state.purchases = [purch_info]
            else:
                state.purchases.append(purch_info)

            time.sleep(random.uniform(1, 5))

        # Set state date/time for when the next purchase (or burst purchase) should be
        # executed.
        if state.num_complete >= cfg.purchases:
            # All purchases complete, set next purchase date to the next month. Wrap
            # around month and increase year if applicable.
            year = now.year+1 if now.month == 12 else now.year
            month = now.month+1 if now.month < 12 else 1
            day = min_day
        else:
            # There are purchases left in the month, set to the next day.
            new_date = now + timedelta(days=1)
            year, month, day = (new_date.year, new_date.month, new_date.day)

            if now.month != new_date.month:
                # Not all purchases were complete so raise error
                logger.error(f"Did not complete all purchases this month.")

            if new_date.day > max_day:
                # Not all purchases can be complete because the next day exceeds the
                # maximum day configured for a month. Raise an error and set next
                # purchase day to first valid day the following month.
                logger.error(
                    f"Did not complete all purchases this month because the next day"
                    f" ({new_date.day}) > max configured day ({max_day}). Setting next"
                    " purchase date to the following month."
                )
                year = now.year+1 if now.month == 12 else now.year
                month = now.month+1 if now.month < 12 else 1
                day = min_day

        # TODO: add some randomness to start time
        state.next_purchase_date = now.replace(
            year=year,
            month=month,
            day=day,
            hour=8,
            minute=0,
            second=0,
            microsecond=0
        )
        logger.info(
            f"Set next purchase date for '{cfg.name}' to {state.next_purchase_date}"
        )

        return state

    def run(self):
        for config in self._configs:
            # Get the state of the config from the database/cache
            state = self.get_state(config)
            min_day, max_day = state.config.days

            # Run purchase logic only if we have purchases left in the month or if we're
            # within month boundaries for purchasing.
            now = datetime.now()
            if (
                min_day <= now.day <= max_day
                and now >= state.next_purchase_date
                and state.num_complete < state.config.purchases
            ):
                state = self.run_purchases(state)

                # Update the state in the database/cache
                save_state(state, state.config.name, self._db_file)
            else:
                logger.debug(
                    f"Skipping reload for '{state.config.name}' because today is outside"
                    f" of day boundaries ({state.config.days}), we have not passed next"
                    f" purchase date ({state.next_purchase_date}), or we have completed"
                    f" all purchases ({state.num_complete}/{state.config.purchases})."
                )
