"""Config file parser.

These classes and dataclasses are for handling the parsing of configuration
file parsing and validation.
"""

import logging
import yaml
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Callable, List, Optional, Union, Sequence, Tuple


logger = logging.getLogger(__name__)


@dataclass
class ReloadConfig:
    """Dataclass for representing a gift card reload parameters for a specific card.

    This dataclass is used to represent the parameters for representing the desired
    parameters for conducting gift card reloads.
    """

    name: str
    """Name of reload."""

    username: str
    """Username for login."""

    password: str
    """Password for login."""

    card: str
    """Card number for verification."""

    purchases: int
    """Number of purchases to complete per month."""

    amounts: Tuple[float, float]
    """"Minimum and maximum range of amounts to reload.

    This is in format (min,max). To set a single amount instead of a range, set min and
    max to the same value.
    """

    days: Tuple[int, int]
    """Minimum and maximum range for days to reload.

    This is in format (min,max). To set a single day instead of a range, set min and max
    to the same value.
    """


# TODO: Add schema validator using jsonschema
def parse_config(file: Union[str, PurePath]) -> Sequence[ReloadConfig]:
    """Parse YAML configuration file for card and reload information.

    This parses YAML configuration files for reload information and adds each card to a
    list.

    Args:
        file:
            File to parse for card configuration information.
    """
    logger.info(f"Parsing configuration file '{file}'")
    configs: List[ReloadConfig] = []

    with open(file) as f:
        data = yaml.safe_load(f)

    for card in data["cards"]:
        cfg: ReloadConfig

        # Get name/alias of reload
        cfg.name = card["name"]
        logger.info(f"Found card reload named '{cfg.name}', adding config.")

        # Get credentials
        cfg.username, cfg.password = card["credentials"].split(":")

        # Get card number
        cfg.card = card["card"]

        # Get purchases
        cfg.purchases = card["purchases"]

        # Get amount limits
        cfg.amounts = tuple(card["amount_limits"])

        # Get day limits
        if "day_limits" in card:
            cfg.days = tuple(card["day_limits"])
        else:
            cfg.days = (None, None)

        # add to list
        configs.append(cfg)

    return configs
