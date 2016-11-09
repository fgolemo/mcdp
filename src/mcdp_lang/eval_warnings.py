from mocdp import logger

class MCDPWarnings:
    LANGUAGE_REFERENCE_OK_BUT_IMPRECISE = 'Language imprecise'
    
def warn_language(element, which, msg, context):
    """
        element: a namedtuplewhere
        which: one of the strings
        msg: a string
    """
    where = element.where
    msg = msg + '\n' + str(where)
    logger.debug(msg)
