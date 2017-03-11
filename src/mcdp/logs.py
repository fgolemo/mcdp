import logging
logging.basicConfig()
logger = logging.getLogger('mcdp')
logger.setLevel(logging.DEBUG)


logger_access = logging.getLogger('mcdp.access')
logger_access.setLevel(logging.INFO)