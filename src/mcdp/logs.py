import logging
from logging import Logger, StreamHandler, Formatter

FORMAT = "[%(filename)15s:%(lineno)-4s - %(funcName)-15s ] %(message)s"


if Logger.root.handlers:  # @UndefinedVariable
    for handler in Logger.root.handlers:  # @UndefinedVariable
        if isinstance(handler, StreamHandler):
            formatter = Formatter(FORMAT)
            handler.setFormatter(formatter)
else:
    logging.basicConfig(format=FORMAT)


logger = logging.getLogger('mcdp')
logger.setLevel(logging.DEBUG)

# temporary stuff - instead of print()
logger_tmp = logger.getChild('tmp')
logger_access = logger.getChild('access')
logger_access.setLevel(logging.INFO)
logger_performance = logger.getChild('performance')
