#!/usr/bin/env python3

import logging
import subprocess
from os import chdir
from os.path import dirname
from typing import NoReturn

from PyLoadBar import load

chdir(dirname(__file__))

__version__ = '0.1.0'

#<--------------------------------------------------------------------------->#
# Log activity from file.
mainLogger = logging.getLogger(__name__)
mainLogger.setLevel(logging.INFO)

# Log activity from upgrade script `global_upgrade.ps1`.
processLogger = logging.getLogger('Subprocess')
processLogger.setLevel(logging.INFO)

# Handler for pre/post upgrade subprocess.
mainFormatter = logging.Formatter('[{asctime} :: {levelname} :: Line: {lineno}] - {message}\n', style='{')
mainHandler = logging.FileHandler('./logs/output.log')
mainHandler.setFormatter(mainFormatter)

# Handler for during upgrade subprocess
processFormatter = logging.Formatter('[{asctime} :: {levelname} :: {funcName.upper()}] - {message}\n', style='{')
processHandler = logging.FileHandler('./logs/output.log')
processHandler.setFormatter(processFormatter)

# Add handlers to both loggers.
mainLogger.addHandler(mainHandler)
processLogger.addHandler(processHandler)
#<--------------------------------------------------------------------------->#

textborder: str = f'\n<{"*" * 120}>\n'

def upgrade():
    """Upgrade outdated pip packages.

    ---

    Parameters:
        :return: start subprocess to upgrade any outdated globally-installed pip packages.
        :rtype: None
    """
    script_p = subprocess.Popen(['powershell.exe', './scripts/upgrade_pip_pkgs.ps1'], stdout=subprocess.PIPE, stderr = subprocess.STDOUT)
    with script_p.stdout:
        try:
            for line in iter(script_p.stdout.readline, b''):
                processLogger.info(line.decode('utf-8').strip())
                print(line.decode('utf-8').strip())
            mainLogger.info('Successfully completed global PIP package upgrade!')
            return exitProgram(0)
        except subprocess.CalledProcessError as e:
            mainLogger.warning(f'An error occurred during execution of upgrade subprocess:\n{str(e)}')
            print(f'An error occurred during execution of upgrade subprocess:\n{str(e)}')
            return exitProgram(1)


def exitProgram(exitcode: int) -> NoReturn | None:
    """Close window and exit program.

    ---

    Parameters:
        :param exitcode: reflects whether program exit was due to successful or failed operation.
        :type exitcode: int
        :return: exits program based on exit-code.
        :rtype: NoReturn
    """
    mainLogger.info('Preparing to exit...')
    load('Preparing to exit...', 'Exiting program...', enable_display=False)
    mainLogger.info(f'Closing log file...{textborder}')
    return exit(exitcode)


def main() -> NoReturn | None:
    """Program entry point.

    # DO NOT CALL MANUALLY.

    ---

    Parameters:
        :return: starts program and event flow.
        :rtype: NoReturn | None
    """
    mainLogger.info(f'Welcome to UpgradePipPkgs {__version__}!')
    while True:
        mainLogger.info('Display upgrade prompt...')
        prompt: str = input(f'{"*"*50}\n| > Upgrade all globally installed PIP packages? |\n| > Enter [Y] to begin upgrade process.          |\n| > Enter [N] to exit.                           |\n{"*"* 50}\n>>> ')
        match prompt.lower():
            case 'y':
                upgrade()
            case 'n':
                return exitProgram(0)
            case _:
                mainLogger.warning(f'Incorrect response from input:\n> Incorrect response: "{prompt}".\n> Accepted values are limited to: "Y" or "N".\n> Please try again.')
                print(f'\n> Incorrect response: "{prompt}".\n> Accepted values are limited to: "Y" or "N".\n> Please try again.\n')

if __name__ == '__main__':
    main()
