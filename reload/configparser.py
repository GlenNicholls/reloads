"""Config file parser.

These classes and dataclasses are for handling the parsing of configuration
file parsing and validation.
"""

import logging
import random
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
    """"Range of amounts to reload.

    This is in format (min,max). To set a single amount instead of a range, set min and
    max to the same value.
    """

    burst: bool = False
    """Burst purchases.

    When true, randomly select an amount of purchases to run between 1 and
    :data:`reload/configparser.ReloadConfig.purchases`. Useful to add some randomness.
    to purchasing.

    .. note::
        When this is enabled, the time between purchases will be random between 1 and
        5 seconds.
    """

    days: Optional[Tuple[int, int]] = (1, 28)
    """Range for days that reloads can be run on.

    This is in format (min,max). This defaults to (1,28) to account for February.
    """


    def rand_amount(self) -> float:
        """Get a random amount between min/max rounded to 2 decimal places."""
        return round(random.uniform(self.amounts[0], self.amounts[1]), 2)


    def rand_day(self) -> int:
        """Get a random day between min/max."""
        return random.randint(self.days[0], self.days[1])


    def rand_burst(self, num_complete: int) -> int:
        """Get a random amount of purchases to run.

        This will use ``num_complete`` to ensure the value provided does not exceed the
        number of purchases to complete each month.

        Args:
            num_complete:
                The number of purchases already complete for the month.
        """
        return random.randint(1, self.purchases-num_complete)


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
        name = card["name"]
        logger.info(f"Found card reload named '{name}', adding config.")

        if "day_limits" in card:
            days = tuple(card["day_limits"])
        else:
            days = (None, None)

        cfg = ReloadConfig(
            name=name,
            username=card["credentials"].split(":")[0],
            password=card["credentials"].split(":")[1],
            card=card["card"],
            purchases=card["purchases"],
            amounts=tuple(card["amount_limits"]),
            days=days,
        )

        # add to list
        configs.append(cfg)

    return configs
