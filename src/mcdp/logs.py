import logging
logging.basicConfig()
logger = logging.getLogger('mcdp')
logger.setLevel(logging.DEBUG)


logger_access = logging.getLogger('mcdp.access')
logger_access.setLevel(logging.INFO)

logger_performance = logging.getLogger('mcdp.performance')
logger_performance.setLevel(logging.DEBUG)