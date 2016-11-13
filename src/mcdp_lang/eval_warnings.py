from mocdp import logger
from contracts.utils import indent
from collections import namedtuple
from mocdp.exceptions import DPInternalError

class MCDPWarnings:
    LANGUAGE_REFERENCE_OK_BUT_IMPRECISE = 'Language imprecise'
    LANGUAGE_CONSTRUCT_DEPRECATED = 'Deprecated construct'
    LANGUAGE_AMBIGUOS_EXPRESSION = 'Ambiguous expression'
    
    
MCDPWarning = namedtuple('MCDPWarning', 'which where msg')


def warn_language(element, which, msg, context):
    """
        element: a namedtuplewhere
        which: one of the strings
        msg: a string
    """
    where = element.where
    msg2 = msg.strip() + '\n\n' + indent(str(where), ' '*4)
    logger.debug(msg2)
    
    if context is not None:
        w = MCDPWarning(which=which,where=where,msg=msg)
        context.warnings.append(w)
    else:
        msg = 'Context is None so I cannot record this.'
        raise DPInternalError(msg )
        logger.debug(msg)
#     setattr(element, 'warning', msg)
