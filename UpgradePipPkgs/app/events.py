import subprocess
import sys
from msvcrt import getch
from typing import NoReturn

from alive_progress import alive_bar
from PyLoadBar import PyLoadBar
from UpgradePipPkgs.app import loggers

textborder: str = f'\n<{"*" * 121}>\n'  # Text border.

main_log = loggers.logger_main
upgrade_log = loggers.logger_upgrade
file_log = loggers.logger_file

exit_seq: PyLoadBar = PyLoadBar(
    bar_sequence=False)  # Initialize exit load-sequence


def get_outdated_pkgs() -> list[str]:
    """Retrieve outdated pip packages using a subprocess to run the command `pip list --outdated`.

    ---

    :return: list of outdated pip packages
    :rtype: :class:`list`[:class:`str`]
    """

    outdated_pkgs: list = []  # list of outdated pip packages

    try:
        upgrade_log.info('Retrieving outdated global pip packages...')

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

    except subprocess.CalledProcessError:
        print()  # newline
        main_log.error(
            f'An error occurred during execution of "get_outdated_pkgs" subprocess...\n',
            exc_info=True)

    finally:
        print()  # newline
        outdated_pkgs = get_outdated.stdout.decode('utf-8').splitlines()[2:]
        upgrade_log.info(f'Outdated packages detected = {len(outdated_pkgs)}.')

        return outdated_pkgs


def upgrade_outdated(outdated_pkgs: list) -> (tuple[list, list]):
    """Run subprocess `pip install --upgrade {pkg}` for all packages in `outdated_pkgs`.

    ---

    :param outdated_pkgs: list containing found outdated global pip packages.
    :type outdated_pkgs: :class:`list`
    :return: results of pip package upgrade.
    :rtype: :class:`tuple`[:class:`list`, :class:`list`]
    """

    upgrade_log.info('Upgrading outdated pip packages...')
    upgrade_log.info(
        '      No. Package            Version           Latest           Type  Status  '
    )
    upgrade_log.info(
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

            try:
                pkgname, ver, latest, setuptype = i.split()
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
            except subprocess.CalledProcessError:
                errorlist.append(pkgname)

                upgrade_log.info(
                    '{0:<4}{1:<19}{2:<18}{3:<17}{4:<6}{5:<8}'.format(
                        count, pkgname, ver, latest, setuptype, 'FAILED'))

                file_log.error(
                    f'An error occurred during execution of "upgrade_outdated" subprocess...\n',
                    exc_info=True)

            else:  # no error
                for line in upgrade_outdated.stdout.decode(
                        'utf-8').splitlines():

                    # display upgrade results.
                    if 'Successfully installed' in line:
                        upgradelist.append(pkgname)
                        upgrade_log.info(
                            '{0:<4}{1:<19}{2:<18}{3:<17}{4:<6}{5:<8}'.format(
                                count, pkgname, ver, latest, setuptype,
                                'UPGRADED'))

    return upgradelist, errorlist


def upgrade_all() -> None:
    """Start subprocess to pass command `pip install --upgrade {pkgname}` for all installed pip packages.

    ---

    :return: attempt to upgrade all pip packages
    :rtype: `None`
    """

    upgradelist: list = []

    upgrade_log.info('Upgrading outdated pip packages "brute force" 1 by 1...')

    # pass command `pip install --upgrade {pkgname}` for all installed pip packages.
    upgrade_script: subprocess.Popen[bytes] = subprocess.Popen(
        ['powershell.exe', 'app/scripts/upgrade_all.ps1'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    with upgrade_script.stdout as process:
        try:

            # Enable progress bar.
            with alive_bar(receipt=False, stats=False) as bar:

                # Display process output
                for line in iter(process.readline, b''):
                    upgrade_log.info(line.decode('utf-8').strip())

                    # update progress bar
                    if 'Successfully installed' in line.decode('utf-8'):
                        upgradelist.append(line.decode('utf-8').strip())
                        bar()

            upgrade_log.info(
                'Successfully completed global pip package upgrade!')
            upgrade_log.info(f'Upgraded packages = {len(upgradelist)}.')

            for count, _ in enumerate(upgradelist, start=1):
                upgrade_log.info(f'{count}. {_}')

            print('\nEnter any key to exit...\n')
            getch()

            return program_exit(0)

        # Exception handling for error returned from subprocess.
        except subprocess.CalledProcessError:
            upgrade_log.error(
                'An error occurred during execution of "upgrade_all" subprocess...',
                exc_info=True)

            return program_exit(1)


def program_exit(exitcode: int) -> NoReturn | None:
    """Close window and exit program.

    ---

    :param exitcode: code reflecting whether program exit was due to successful or failed operation.
    :type exitcode: :class:`int`
    :return: exits program with passed `exitcode`.
    :rtype: :class:`NoReturn` | `None`
    """

    file_log.debug('Preparing to exit...')

    # display exit text animation
    exit_seq.start('Preparing to exit',
                   'Exiting...',
                   iter_total=5,
                   txt_iter_speed=0.25)
    file_log.debug(f'Closing log file...{textborder}')

    return exit(exitcode)


class menu:
    """Display menu and prompt user for selection.

    ---

    Menu options:

    ```python
        1. Upgrade outdated pip packages.
        2. "Brute-force-upgrade" all packages (one by one).
        3. Exit.
    ```
    ---

    :return: user selection.
    :rtype: `None`
    """

    def __init__(self) -> None:
        self.menu_options: list = [
            'Upgrade outdated pip packages',
            '"Brute-force-upgrade" all packages (one by one)', 'Exit'
        ]

    def display(self) -> None:
        """Display menu and prompt user for selection.
        """
        file_log.debug('Displaying user options menu...')

        for count, i in enumerate(self.menu_options, start=1):
            print(f'|\n|{count}. {i}')

    @staticmethod
    def get_input() -> int:
        """Prompt user for selection.
        """
        while True:
            try:
                prompt: str = input(
                    f'|{"*"*78}|\n| > Upgrade all outdated global pip packages?                                  |\n| > Enter [1] to get list of outdated pip pkgs before upgrading list contents. |\n| > Enter [2] to "brute-force" upgrade pip pkgs (longer but more verbose).     |\n| > Enter [3] to exit program.                                                 |\n|{"*"* 78}|\n>>> '
                )
                print()
                return int(prompt)

            except ValueError:
                main_log.warning(
                    f'Incorrect response: "{prompt}".\n==> Accepted values are limited to: "1", "2" or "3".\n==> Please try again.'
                )
                continue

    def _logic(self) -> bool:
        """
        It's a function that prompts the user to choose between three options, and then executes the chosen
        option
        :return: The return value of the function.
        :rtype: :class:`bool`
        """

        opt: options = options()

        while True:
            try:
                prompt = self.get_input()

                if prompt == 1:
                    return opt.option_1()

                elif prompt == 2:
                    return opt.option_2()

                elif prompt == 3:
                    return True

                else:
                    main_log.warning(
                        f'Incorrect response: "{prompt}".\n==> Accepted values are limited to: "1", "2" or "3".\n==> Please try again.'
                    )

            except KeyboardInterrupt:
                main_log.warning(
                    'Keyboard interrupt was triggered by user during menu process...',
                    exc_info=True)
                return False
class options:
    """Contains all options from main menu."""

    @staticmethod
    def option_1() -> bool:
        """Upgrade outdated pip packages."""

        file_log.debug('User selected option 1.')
        try:
            outdated_pkgs: list[str] = get_outdated_pkgs()

            if len(outdated_pkgs):
                upgradelist, errorlist = upgrade_outdated(outdated_pkgs)
                total: int = len(outdated_pkgs)
                upgrade_log.info('Successfully completed upgrade process!')
                upgrade_log.info('SUMMARY:')
                upgrade_log.info(
                    f'No. of upgrade errors    = {len(errorlist)}/{total}')
                upgrade_log.info(
                    f'No. of packages upgraded = {len(upgradelist)}/{total}')
            else:
                main_log.info('No outdated packages found!')

            print('\nPress any key to exit...\n')
            getch()
            return True

        except KeyboardInterrupt:
            main_log.warning(
                'Keyboard interrupt was triggered by user during execution of "upgrade_outdated" subprocess...',
                exc_info=True)
            return False

        except Exception:
            upgrade_log.error(
                'An error occurred during execution of "upgrade_outdated" subprocess...',
                exc_info=True)
            return False

    @staticmethod
    def option_2() -> bool:
        """Upgrade all packages one-by-one.

        - "Brute-force-upgrade".
        """

        file_log.debug('User selected option 2.')
        try:
            upgrade_all()
            return True
        except KeyboardInterrupt:
            main_log.warning(
                'Keyboard interrupt was triggered by user during execution of "upgrade_all" subprocess...',
                exc_info=True)
            return False

        except Exception:
            upgrade_log.error(
                'An error occurred during execution of "upgrade_all" subprocess...',
                exc_info=True)
            return False
