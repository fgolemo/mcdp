from mocdp import logger
from contracts.utils import indent
from collections import namedtuple
from mocdp.exceptions import DPInternalError

class MCDPWarnings:
    LANGUAGE_REFERENCE_OK_BUT_IMPRECISE = 'Language imprecise'
    LANGUAGE_CONSTRUCT_DEPRECATED = 'Deprecated construct'
    LANGUAGE_AMBIGUOS_EXPRESSION = 'Ambiguous expression'
    
    
class MCDPWarning(namedtuple('MCDPWarning', 'which where msg')):
    def format_user(self):
        s = self.msg
        if self.where:
            s += '\n\n'
            s += self.where.__str__()
        return s
    
class MCDPNestedWarning(namedtuple('MCDPNestedWarning', 'where msg warning')):
    def format_user(self):
        s = self.msg
        if self.where:
            s += '\n\n'
            s += self.where.__str__()
        else:
            s += '\n\n(no where)' 
        s += '\n' + indent(self.warning.format_user(), ' > ')
        return s

def warnings_copy_from_child_make_nested(context0, context, msg, where):
    for w in context.warnings:
        w2 = MCDPNestedWarning(msg=msg, where=where, warning=w)
        context0.warnings.append(w2)
    
def warnings_copy_from_child(context0, context):
    for w in context.warnings:
        context0.warnings.append(w)


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
