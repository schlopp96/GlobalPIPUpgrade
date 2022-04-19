#!/usr/bin/env python3

import logging
import subprocess
import sys
from os import chdir
from os.path import dirname
from typing import NoReturn

from PyLoadBar import load



chdir(dirname(__file__))

__version__ = '0.1.0'

textborder: str = f'\n<{"*" * 120}>\n'

def config_logs(__file__) -> tuple[logging.Logger, logging.Logger]:
    """Set program logging configuration and generate loggers.

---

    Parameters:
        :param __file__: file to be logged.
        :type __file__: Any
        :return: program logging configuration.
        :rtype: tuple[Logger, Logger]
    """
    # Log activity from file.
    mainLogger = logging.getLogger(__file__)
    mainLogger.setLevel(logging.INFO)

# Log activity from upgrade script `global_upgrade.ps1`.
    processLogger = logging.getLogger('Subprocess')
    processLogger.setLevel(logging.INFO)

# Handler for pre/post upgrade subprocess.
    mainFormatter = logging.Formatter(
    '[{asctime} :: {levelname} :: Line: {lineno}] - {message}\n', style='{')
    mainHandler = logging.FileHandler('./logs/output.log')
    mainHandler.setFormatter(mainFormatter)

# Handler for during upgrade subprocess
    processFormatter = logging.Formatter(
    '[{asctime} :: {levelname} :: {funcName}] - {message}\n', style='{')
    processHandler = logging.FileHandler('./logs/output.log')
    processHandler.setFormatter(processFormatter)

# Add handlers to both loggers.
    mainLogger.addHandler(mainHandler)
    processLogger.addHandler(processHandler)

    return mainLogger,processLogger

# Set logger names.
mainLogger, processLogger = config_logs(__file__)

def get_outdated_pkgs():
    """Subprocess to retrieve outdated global pip packages using `pip list --outdated`.

    ---

    Parameters:
        :return: retrieve and pass outdated global pip packages to a list to be upgraded.
        :rtype: (List[str] | None)
    """
    outdated_pkgs =[]

    try:
        processLogger.info('Retrieving outdated global pip packages...')
        print('Retrieving outdated global pip packages...\n')
        cmd = [sys.executable, '-m', 'pip', 'list', '--outdated']
        get_outdated = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr = subprocess.STDOUT)

    except subprocess.CalledProcessError as err:
        mainLogger.warning(f'An error occurred during execution of "get_outdated_pkgs" subprocess:\n--> {str(err)}')
        print(f'An error occurred during execution of "get_outdated_pkgs" subprocess:\n--> {str(err)}')
    else:
        outdated_pkgs = list(get_outdated.stdout.decode('utf-8').splitlines()[2:])
        processLogger.info(f'Outdated packages detected = {len(outdated_pkgs)}.')
        print(f'Outdated packages detected = {len(outdated_pkgs)}.')
        return outdated_pkgs

def upgrade_outdated(outdated_pkgs: list):
    """Run subprocess `pip install --upgrade {pkg}` for all packages in `outdated_pkgs`.

    ---

    Parameters:
        :param outdated_pkgs: list containing found outdated global pip packages.
        :type outdated_pkgs: list
        :return: subprocess to upgrade all found outdated global pip packages.
        :rtype: tuple[list, list] | None
    """
    processLogger.info('Upgrading outdated pip packages...')
    print('Upgrading outdated pip packages...\n')

    processLogger.info('No. Package            Version           Latest           Type  Status  ')
    processLogger.info('--- ------------------ ----------------- ---------------- ----- --------')

    print('No. Package            Version           Latest           Type  Status  ')
    print('--- ------------------ ----------------- ---------------- ----- --------')

    upgradelist = []
    errorlist = []
    for count, i in enumerate(outdated_pkgs, start=1):
        pkgname, ver, latest, setuptype = i.split()
        try:
            cmd = [sys.executable,'-m','pip','install','--upgrade', pkgname]
            upgrade_outdated = subprocess.run( cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
        except subprocess.CalledProcessError as err:
            errorlist.append(pkgname)

            mainLogger.warning('{0:<4}{1:<19}{2:<18}{3:<17}{4:<6}{5:<8}'.format(
                count,pkgname,ver,latest,setuptype,'FAILED'))
            mainLogger.warning(f'An error occurred during execution of "upgrade_outdated" subprocess:\n--> {str(err)}')

            print('{0:<4}{1:<19}{2:<18}{3:<17}{4:<6}{5:<8}'.format(
                count,pkgname,ver,latest,setuptype,'FAILED'))
            print(f'An error occurred during execution of "upgrade_outdated" subprocess:\n--> {str(err)}')
            return exitProgram(1)
        else:
            for line in upgrade_outdated.stdout.decode('utf-8').splitlines():
                if 'Successfully installed' in line:
                    upgradelist.append(pkgname)
                    processLogger.info('{0:<4}{1:<19}{2:<18}{3:<17}{4:<6}{5:<8}'.format(
                        count,pkgname,ver,latest,setuptype,'UPGRADED'))
                    print('{0:<4}{1:<19}{2:<18}{3:<17}{4:<6}{5:<8}'.format(
                        count,pkgname,ver,latest,setuptype,'UPGRADED'))
    return upgradelist, errorlist

def upgrade_all():
    """Run subprocess `pip install --upgrade {pkgname}` for all installed global pip packages.

    ---

    Parameters:
        :return: subprocess to upgrade all outdated global pip packages using "brute force".
        :rtype: None
    """
    processLogger.info('Upgrading outdated pip packages using "brute force"...')
    print('Upgrading outdated pip packages using "brute force"...\n')

    script_p = subprocess.Popen(['powershell.exe', './scripts/force_upgrade_pip_pkgs.ps1'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with script_p.stdout:
        try:
            for line in iter(script_p.stdout.readline, b''):
                processLogger.info(line.decode('utf-8').strip())
                print(line.decode('utf-8').strip())
            mainLogger.info('Successfully completed global pip package upgrade!')
            print('\nSuccessfully completed global pip package upgrade!\n')
            input('\nPress Enter to Exit.')
            return exitProgram(0)
        except subprocess.CalledProcessError as err:
            mainLogger.warning(f'An error occurred during execution of "upgrade_all" subprocess:\n--> {str(err)}')
            print(f'An error occurred during execution of "upgrade_all" subprocess:\n--> {str(err)}')
            return exitProgram(1)


def exitProgram(exitcode: int) -> NoReturn | None:
    """Close window and exit program.

    ---

    Parameters:
        :param exitcode: code reflecting whether program exit was due to successful or failed operation.
        :type exitcode: int
        :return: exits program with passed `exitcode`.
        :rtype: NoReturn | None
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
        :return: starts program event flow.
        :rtype: NoReturn | None
    """
    mainLogger.info(f'Welcome to UpgradePipPkgs {__version__}!')
    while True:
        mainLogger.info('Displaying user options menu...')
        prompt: str = input(f'|{"*"*78}|\n| > Upgrade all outdated global pip packages?                                  |\n| > Enter [1] to get list of outdated pip pkgs before upgrading list contents. |\n| > Enter [2] to "brute-force" upgrade outdated pip pkgs (longer but safer.)   |\n| > Enter [3] to exit program.                                                 |\n|{"*"* 78}|\n>>> ')
        match prompt.lower():
            case '1':
                try:
                    print()
                    outdated_pkgs = get_outdated_pkgs()
                    if len( outdated_pkgs ):
                        upgradelist, errorlist  = upgrade_outdated(outdated_pkgs)
                        total=len(outdated_pkgs)
                        mainLogger.info('Successfully completed upgrade process!')
                        mainLogger.info('SUMMARY:')
                        mainLogger.info(f'No. of packages upgraded = {len(upgradelist)}/{total}')
                        mainLogger.info(f'No. of upgrade errors    = {len(errorlist)}/{total}')
                        print('\nSuccessfully completed upgrade process!')
                        print('\nSUMMARY:')
                        print(f'No. of packages upgraded = {len(upgradelist)}/{total}')
                        print(f'No. of upgrade errors    = {len(errorlist)}/{total}')
                        input('\nPress Enter to Exit.')
                        return exitProgram(0)
                    else:
                        mainLogger.info('No outdated packages found!')
                        print('No outdated packages found!')
                        input('\nPress Enter to Exit.')
                        return exitProgram(0)
                except KeyboardInterrupt:
                    mainLogger.warning(f'An error occurred during execution of "upgrade_outdated" subprocess:\n==> Keyboard interrupt was triggered by user.')
                    print(f'\nAn error occurred during execution of "upgrade_outdated" subprocess:\n==> Keyboard interrupt was triggered by user...\n')
                    return exitProgram(1)
            case '2':
                try:
                    print()
                    upgrade_all()
                    return exitProgram(0)
                except KeyboardInterrupt:
                    mainLogger.warning(f'An error occurred during execution of "upgrade_all" subprocess:\n==> Keyboard interrupt was triggered by user.')
                    print(f'\nAn error occurred during execution of "upgrade_all" subprocess:\n==> Keyboard interrupt was triggered by user...\n')
                    return exitProgram(1)
            case '3':
                return exitProgram(0)
            case _:
                mainLogger.warning(f'Incorrect response from input:\n==> Incorrect response: "{prompt}".\n==> Accepted values are limited to: "Y" or "N".\n==> Please try again.')
                print(f'\n==> Incorrect response: "{prompt}".\n==> Accepted values are limited to: "Y" or "N".\n==> Please try again.\n')

if __name__ == '__main__':
    main()
