#!/usr/bin/env python3

import logging

from reload.api import Reload, cli
from reload.utils import config_logger

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # Setup CLI and parse args
    parser = cli()
    args = parser.parse_args()

    # Configure terminal/file logger
    log_level = logging.DEBUG if args.verbose else logging.INFO
    config_logger(filename=args.log_file, level=log_level)

    # Run reloads.
    reload = Reload(config_file=args.config_file)#, prompt_user=args.prompt)
    reload.run(args.force_reload)
