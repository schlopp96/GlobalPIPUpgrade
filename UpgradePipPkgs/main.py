#!/usr/bin/env python3

import logging
import subprocess
import sys
from msvcrt import getch
from os import chdir
from os.path import dirname
from typing import NoReturn

from PyLoadBar import PyLoadBar
from alive_progress import alive_bar

sys.path.insert(0, dirname(
    dirname(__file__)))  # Ensure main module can be found by Python.

chdir(dirname(__file__))  # Change working directory to main module.

__version__ = '0.3.0'  # Version of main module.

textborder: str = f'\n<{"*" * 121}>\n'  # Text border.

exit_seq: PyLoadBar = PyLoadBar(
    'Preparing to exit', 'Exiting...',
    enable_bar=False)  # Initialize exit load-sequence.


def config_logs() -> tuple[logging.Logger, logging.Logger, logging.Logger]:
    """Generate program loggers.

    ---

    :type file: :class:`str`, optional
    :return: program logging configuration.
    :rtype: :class:`tuple`[:class:`Logger`, :class:`Logger`, :class:`Logger`]
    """

    # Log activity from file.
    logger_main: logging.Logger = logging.getLogger('MAIN')
    logger_main.setLevel(logging.INFO)

    # Log activity from powershell script `upgrade_all.ps1`.
    logger_upgrade: logging.Logger = logging.getLogger('UPGRADE')
    logger_upgrade.setLevel(logging.INFO)

    # Log other messages to log file.
    logger_file: logging.Logger = logging.getLogger('LOG')
    logger_file.setLevel(logging.DEBUG)

    # Handler for pre/post upgrade subprocess.
    formatter_main: logging.Formatter = logging.Formatter(
        '[{asctime} :: {name} :: {levelname}] - {message}\n',
        style='{',
        datefmt="%Y-%m-%d - %H:%M:%S")
    file_handler_main: logging.FileHandler = logging.FileHandler(
        './logs/pkg_upgrade_log.log')
    stream_handler_main: logging.StreamHandler = logging.StreamHandler()

    file_handler_main.setFormatter(formatter_main)
    stream_handler_main.setFormatter(formatter_main)

    # Handler for upgrade subprocess
    formatter_upgrade: logging.Formatter = logging.Formatter(
        '[{asctime} :: {name} :: {levelname}] - {message}\n',
        style='{',
        datefmt="%Y-%m-%d - %H:%M:%S")
    file_handler_upgrade: logging.FileHandler = logging.FileHandler(
        './logs/pkg_upgrade_log.log')
    stream_handler_upgrade: logging.StreamHandler = logging.StreamHandler()

    file_handler_upgrade.setFormatter(formatter_upgrade)
    stream_handler_upgrade.setFormatter(formatter_upgrade)

    # Handler for file logging.
    formatter_file: logging.Formatter = logging.Formatter(
        '[{asctime} :: {name} :: {levelname}] - {message}\n',
        style='{',
        datefmt="%Y-%m-%d - %H:%M:%S")
    file_handler_file: logging.FileHandler = logging.FileHandler(
        './logs/pkg_upgrade_log.log')

    file_handler_file.setFormatter(formatter_file)

    # Add handlers to loggers.
    logger_main.addHandler(file_handler_main)
    logger_main.addHandler(stream_handler_main)

    logger_upgrade.addHandler(file_handler_upgrade)
    logger_upgrade.addHandler(stream_handler_upgrade)

    logger_file.addHandler(file_handler_file)

    return logger_main, logger_upgrade, logger_file


# Generate loggers.
logger_main, logger_upgrade, logger_file = config_logs()


def get_outdated_pkgs() -> list[str]:
    """Retrieve outdated pip packages using a subprocess to run the command `pip list --outdated`.

    ---

    :return: list of outdated pip packages
    :rtype: :class:`list`[:class:`str`] | None
    """

    outdated_pkgs: list = []

    try:
        logger_upgrade.info('Retrieving outdated global pip packages...')

        # Enable progress bar.
        with alive_bar(total=None,
                       stats=False,
                       elapsed=False,
                       monitor=False,
                       receipt=False):
            cmd: list[str] = [
                sys.executable, '-m', 'pip', 'list', '--outdated'
            ]
            get_outdated: subprocess.CompletedProcess = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)

    except subprocess.CalledProcessError as err:
        print()
        logger_main.error(
            f'An error occurred during execution of "get_outdated_pkgs" subprocess:\n',
            exc_info=err)

    finally:
        print()
        outdated_pkgs = get_outdated.stdout.decode('utf-8').splitlines()[2:]
        logger_upgrade.info(
            f'Outdated packages detected = {len(outdated_pkgs)}.')
        return outdated_pkgs


def upgrade_outdated(outdated_pkgs: list) -> (tuple[list, list]):
    """Run subprocess `pip install --upgrade {pkg}` for all packages in `outdated_pkgs`.

    ---

    :param outdated_pkgs: list containing found outdated global pip packages.
    :type outdated_pkgs: :class:`list`
    :return: results of pip package upgrade.
    :rtype: :class:`tuple`[:class:`list`, :class:`list`] | None
    """

    logger_upgrade.info('Upgrading outdated pip packages...')
    logger_upgrade.info(
        '      No. Package            Version           Latest           Type  Status  '
    )
    logger_upgrade.info(
        '      === ================== ================= ================ ===== ========'
    )

    upgradelist: list = []
    errorlist: list = []

    # Enable progress bar.
    with alive_bar(total=len(outdated_pkgs), stats=False,
                   receipt=False) as bar:

        # iterate through all outdated packages.
        for count, i in enumerate(outdated_pkgs, start=1):

            # Split string into separate individual variables.
            pkgname, ver, latest, setuptype = i.split()

            try:
                # Command to pass to subprocess.
                cmd: list = [
                    sys.executable, '-m', 'pip', 'install', '--upgrade',
                    pkgname
                ]

                # Run upgrade subprocess.
                upgrade_outdated: subprocess.CompletedProcess = subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)

                bar()  # update progress bar

            # upgrade error
            except subprocess.CalledProcessError as err:
                errorlist.append(pkgname)

                logger_upgrade.info(
                    '{0:<4}{1:<19}{2:<18}{3:<17}{4:<6}{5:<8}'.format(
                        count, pkgname, ver, latest, setuptype, 'FAILED'))

                logger_file.debug(
                    f'An error occurred during execution of "upgrade_outdated" subprocess:\n',
                    exc_info=err)

            else:  # no error
                for line in upgrade_outdated.stdout.decode(
                        'utf-8').splitlines():

                    # display upgrade results.
                    if 'Successfully installed' in line:
                        upgradelist.append(pkgname)
                        logger_upgrade.info(
                            '{0:<4}{1:<19}{2:<18}{3:<17}{4:<6}{5:<8}'.format(
                                count, pkgname, ver, latest, setuptype,
                                'UPGRADED'))
    return upgradelist, errorlist


def upgrade_all():
    """Start subprocess to pass command `pip install --upgrade {pkgname}` for all installed pip packages.

    ---

    :return: attempt to upgrade all pip packages
    :rtype: None
    """

    upgradelist: list = []

    logger_upgrade.info(
        'Upgrading outdated pip packages using "brute force"...')

    # pass command `pip install --upgrade {pkgname}` for all installed pip packages.
    upgrade_script: subprocess.Popen[bytes] = subprocess.Popen(
        ['powershell.exe', './scripts/upgrade_all.ps1'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    with upgrade_script.stdout as process:
        try:

            # Enable progress bar.
            with alive_bar(receipt=False) as bar:

                # Display process output
                for line in iter(process.readline, b''):
                    logger_upgrade.info(line.decode('utf-8').strip())

                    # update progress bar
                    if 'Successfully installed' in line.decode('utf-8'):
                        upgradelist.append(line.decode('utf-8').strip())
                        bar()

            logger_upgrade.info(
                'Successfully completed global pip package upgrade!')
            logger_upgrade.info(f'Upgraded packages = {len(upgradelist)}.')

            for count, _ in enumerate(upgradelist, start=1):
                logger_upgrade.info(f'{count}. {_}')

            print('\nEnter any key to exit...\n')
            getch()
            return exitProgram(0)

        # Exception handling for error returned from subprocess.
        except subprocess.CalledProcessError as err:
            logger_upgrade.error(
                'An error occurred during execution of "upgrade_all" subprocess...',
                exc_info=err)

            return exitProgram(1)


def exitProgram(exitcode: int) -> NoReturn | None:
    """Close window and exit program.

    ---

    :param exitcode: code reflecting whether program exit was due to successful or failed operation.
    :type exitcode: :class:`int`
    :return: exits program with passed `exitcode`.
    :rtype: :class:`NoReturn` | None
    """

    logger_file.debug('Preparing to exit...')

    # display exit text animation
    exit_seq.start(3, txt_seq_speed=0.5)
    logger_file.debug(f'Closing log file...{textborder}')
    return exit(exitcode)


def menu() -> bool:
    """Display menu and prompt user for selection.

    ---

    :return: menu text and user selection.
    :rtype: None
    """

    while True:
        logger_file.debug('Displaying user options menu...')
        prompt: str = input(
            f'|{"*"*78}|\n| > Upgrade all outdated global pip packages?                                  |\n| > Enter [1] to get list of outdated pip pkgs before upgrading list contents. |\n| > Enter [2] to "brute-force" upgrade pip pkgs (longer but more verbose).     |\n| > Enter [3] to exit program.                                                 |\n|{"*"* 78}|\n>>> '
        )
        print()

        if prompt == '1':
            try:
                outdated_pkgs: list[str] = get_outdated_pkgs()

                if len(outdated_pkgs):
                    upgradelist, errorlist = upgrade_outdated(outdated_pkgs)
                    total: int = len(outdated_pkgs)
                    logger_upgrade.info(
                        'Successfully completed upgrade process!')
                    logger_upgrade.info('SUMMARY:')
                    logger_upgrade.info(
                        f'No. of upgrade errors    = {len(errorlist)}/{total}')
                    logger_upgrade.info(
                        f'No. of packages upgraded = {len(upgradelist)}/{total}'
                    )

                else:
                    logger_main.info('No outdated packages found!')

                print('\nPress any key to exit...\n')
                getch()
                return True

            except KeyboardInterrupt as err:
                logger_main.warning(
                    'Keyboard interrupt was triggered by user during execution of "upgrade_outdated" subprocess...',
                    exc_info=err)
                return False

        elif prompt == '2':
            try:
                upgrade_all()
                return True

            except KeyboardInterrupt as err:
                logger_main.warning(
                    'Keyboard interrupt was triggered by user during execution of "upgrade_outdated" subprocess...',
                    exc_info=err)
                return False

        elif prompt == '3':
            return True

        else:
            logger_main.info(
                f'Incorrect response: "{prompt}".\n==> Accepted values are limited to: "1", "2" or "3".\n==> Please try again.'
            )


def main() -> NoReturn | None:
    """Program entry point.

    ---

    :return: starts program event flow.
    :rtype: :class:`NoReturn` | None
    """

    logger_main.info(f'Welcome to UpgradePipPkgs {__version__}!')
    return exitProgram(0) if menu() else exitProgram(1)


if __name__ == '__main__':
    main()
