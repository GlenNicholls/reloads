"""Config file parser.

These classes and dataclasses are for handling the parsing of configuration
file parsing and validation.
"""

import yaml
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Callable, List, Optional, Union


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

    min_amount: float
    """"Minimum amount to reload on the gift card purchase."""

    max_amount: float
    """Maximum amount to reload on the gift card purchase."""

    min_day: int
    """Minimum day to complete a purchase."""

    max_day: int
    """Maximum day to complete a purchase."""


def parse_config(self, file: Union[str, PurePath]) -> None:
    """Parse YAML configuration file for card and reload information.

    This parses YAML configuration files for reload information and adds each card to a
    list.

    Args:
        file:
            File to parse for card configuration information.
    """
    configs: List[ReloadConfig] = []

    with open(file) as f:
        data = yaml.safe_load(f)

    for card in data["cards"]:
        cfg: ReloadConfig
        cfg.name = card["name"]

        # Get credentials
        cfg.username, cfg.password = card["credentials"].split(":")

        # Get card number
        cfg.card = card["card"]

        # Get purchases
        cfg.purchases = card["purchases"]

        # Get amount limits
        cfg.min_amount = card["amount_limits"][0]
        cfg.max_amount = card["amount_limits"][1]

        # Get day limits
        if "day_limits" in card:
            cfg.min_day = card["day_limits"][0]
            cfg.max_day = card["day_limits"][1]
        else:
            cfg.min_day = None
            cfg.max_day = None

        # add to list
        configs.append(cfg)

    return configs
