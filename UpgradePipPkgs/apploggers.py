import logging
from os.path import dirname
from os import chdir

chdir(dirname(__file__))

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