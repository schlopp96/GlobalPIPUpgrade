#!/usr/bin/env python3

import sys
from os import chdir
from os.path import dirname
from typing import NoReturn

from UpgradePipPkgs.app import events, loggers

sys.path.insert(0, dirname(
    dirname(__file__)))  # Ensure main module can be found by Python.

chdir(dirname(__file__))  # Change working directory to main module.

__version__ = '0.4.0'  # Version of main module.

logger_main = loggers.logger_main


def main() -> NoReturn | None:
    """Program entry point.

    ---

    :return: starts program event flow.
    :rtype: :class:`NoReturn` | None
    """

    logger_main.info(f'Welcome to UpgradePipPkgs {__version__}!')
    return events.exitProgram(0) if events.menu() else events.exitProgram(1)


if __name__ == '__main__':
    main()
