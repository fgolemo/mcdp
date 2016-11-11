from mocdp import logger
from contracts.utils import indent

class MCDPWarnings:
    LANGUAGE_REFERENCE_OK_BUT_IMPRECISE = 'Language imprecise'
    LANGUAGE_CONSTRUCT_DEPRECATED = 'Deprecated construct'
    LANGUAGE_AMBIGUOS_EXPRESSION = 'Ambiguous expression'
    


def warn_language(element, which, msg, context):
    """
        element: a namedtuplewhere
        which: one of the strings
        msg: a string
    """
    where = element.where
    msg = msg.strip() + '\n\n' + indent(str(where), ' '*4)
    logger.debug(msg)
    
#     setattr(element, 'warning', msg)