# annoying warning from BS4

import logging
from logging import Logger, StreamHandler, Formatter

FORMAT = "%(name)15s|%(filename)15s:%(lineno)-4s - %(funcName)-15s| %(message)s"


if Logger.root.handlers:  # @UndefinedVariable
    for handler in Logger.root.handlers:  # @UndefinedVariable
        if isinstance(handler, StreamHandler):
            formatter = Formatter(FORMAT)
            handler.setFormatter(formatter)
else:
    logging.basicConfig(format=FORMAT)


logger = logging.getLogger('mcdp-docs')
logger.setLevel(logging.DEBUG)

import chardet  # @UnusedImport
logging.getLogger("chardet.universaldetector").setLevel(logging.CRITICAL)
import PIL  # @UnusedImport
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.CRITICAL)


