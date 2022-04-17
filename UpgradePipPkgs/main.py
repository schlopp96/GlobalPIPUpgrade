#!/usr/bin/env python3

import subprocess
from os import chdir
from os.path import dirname
from typing import NoReturn
from applogging import processLogger, mainLogger
from PyLoadBar import load

chdir(dirname(__file__))

__version__ = '0.1.0'

textborder: str = f'\n<{"*" * 120}>\n'

def upgrade():
    """Upgrade global pip packages.

    ---

    Parameters:
        :return: subprocess to upgrade all outdated global pip packages.
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
            mainLogger.warning(f'An error occurred during execution of upgrade subprocess:\n--> {str(e)}')
            print(f'An error occurred during execution of upgrade subprocess:\n--> {str(e)}')
            return exitProgram(1)


def exitProgram(exitcode: int) -> NoReturn | None:
    """Close window and exit program.

    ---

    Parameters:
        :param exitcode: code reflecting whether program exit was due to successful or failed operation.
        :type exitcode: int
        :return: exits program with passed `exitcode`.
        :rtype: NoReturn
    """
    mainLogger.info('Preparing to exit...')
    load('Preparing to exit...', 'Exiting program...', 10, enable_display=False)
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
        mainLogger.info('Displaying menu prompt...')
        prompt: str = input(f'{"*"*50}\n| > Upgrade all globally installed PIP packages? |\n| > Enter [Y] to begin upgrade process.          |\n| > Enter [N] to exit.                           |\n{"*"* 50}\n>>> ')
        match prompt.lower():
            case 'y':
                try:
                    print()
                    return upgrade()
                except KeyboardInterrupt:
                    mainLogger.warning(f'An error occurred during execution of upgrade subprocess:\n==> Keyboard interrupt was triggered by user.')
                    print(f'\nAn error occurred during execution of upgrade subprocess:\n==> Keyboard interrupt was triggered by user...\n')
                    return exitProgram(1)
            case 'n':
                return exitProgram(0)
            case _:
                mainLogger.warning(f'Incorrect response from input:\n==> Incorrect response: "{prompt}".\n==> Accepted values are limited to: "Y" or "N".\n==> Please try again.')
                print(f'\n==> Incorrect response: "{prompt}".\n==> Accepted values are limited to: "Y" or "N".\n==> Please try again.\n')

if __name__ == '__main__':
    main()
