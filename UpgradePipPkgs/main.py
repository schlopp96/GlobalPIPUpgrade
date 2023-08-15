#!/usr/bin/env python3

#UpgradePipPkgs V0.4.2

import sys
from os import chdir
from os.path import dirname
from typing import NoReturn

sys.path.insert(0, dirname(
    dirname(__file__)))  # Ensure module can be found by Python.

chdir(dirname(__file__))  # Change working directory to module.

from UpgradePipPkgs.app import events, loggers

__version__ = '0.4.2'  # Version of main module.

logger_main = loggers.logger_main
menu = events.menu()  # Start program event flow.


def main() -> NoReturn | None:
    """Program entry point.

    ---

    :return: starts program event flow.
    :rtype: :class:`NoReturn` | `None`
    """

    logger_main.info(f'Welcome to UpgradePipPkgs {__version__}!')
    return events.program_exit(0) if menu._logic() else events.program_exit(1)


if __name__ == '__main__':
    main()
