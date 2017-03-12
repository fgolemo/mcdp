import logging

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)

logger = logging.getLogger('mcdp')
logger.setLevel(logging.DEBUG)

logger_tmp = logger.getChild('tmp')
logger_access = logger.getChild('access')
logger_performance = logger.getChild('performance')
