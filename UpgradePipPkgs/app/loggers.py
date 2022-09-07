import logging


def config_logs() -> tuple[logging.Logger, logging.Logger, logging.Logger]:
    """Generate program loggers.

    ---

    :return: program logging configuration.
    :rtype: :class:`tuple`[:class:`logging.Logger`, :class:`logging.Logger`, :class:`logging.Logger`]
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
        '[{asctime} :: {levelname}]\n>> {message}\n',
        style='{',
        datefmt="%Y-%m-%d %H:%M:%S")
    file_handler_main: logging.FileHandler = logging.FileHandler(
        './logs/pkg_upgrade_log.log')
    stream_handler_main: logging.StreamHandler = logging.StreamHandler()

    file_handler_main.setFormatter(formatter_main)
    stream_handler_main.setFormatter(formatter_main)

    # Handler for upgrade subprocess
    formatter_upgrade: logging.Formatter = logging.Formatter(
        '[{asctime} :: {levelname}] - {message}\n',
        style='{',
        datefmt="%Y-%m-%d %H:%M:%S")
    file_handler_upgrade: logging.FileHandler = logging.FileHandler(
        './logs/pkg_upgrade_log.log')
    stream_handler_upgrade: logging.StreamHandler = logging.StreamHandler()

    file_handler_upgrade.setFormatter(formatter_upgrade)
    stream_handler_upgrade.setFormatter(formatter_upgrade)

    # Handler for file logging.
    formatter_file: logging.Formatter = logging.Formatter(
        '[{asctime} :: {levelname}] - {message}\n',
        style='{',
        datefmt="%Y-%m-%d %H:%M:%S")
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
