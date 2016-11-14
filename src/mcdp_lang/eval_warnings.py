from mocdp import logger
from contracts.utils import indent
from collections import namedtuple
from mocdp.exceptions import DPInternalError
from contracts.interface import format_where

class MCDPWarnings:
    LANGUAGE_REFERENCE_OK_BUT_IMPRECISE = 'Language imprecise'
    LANGUAGE_CONSTRUCT_DEPRECATED = 'Deprecated construct'
    LANGUAGE_AMBIGUOS_EXPRESSION = 'Ambiguous expression'
    
def warning_format_where(where):
    wheres = format_where(where, context_before=0, mark=None, arrow=False, 
                      use_unicode=True, no_mark_arrow_if_longer_than=3)
    return wheres
    
    
class MCDPWarning(namedtuple('MCDPWarning', 'which where msg')):
    
    def copy_with_filename(self, f):
        w = self.where.with_filename(f) if self.where else None
        return MCDPWarning(where=w, which=self.which, msg=self.msg)
    
    def format_user(self):
        s = self.msg
        if self.where:
            s += '\n\n'
            s += warning_format_where(self.where)
        return s
    
class MCDPNestedWarning(namedtuple('MCDPNestedWarning', 'where msg warning')):
    
    def copy_with_filename(self, f):
        w = self.where.with_filename(f) if self.where else None
        return MCDPNestedWarning(where=w, warning=self.warning, msg=self.msg)
    
    def format_user(self):
        s = self.msg
        if self.where:
            s += '\n\n'
            s += warning_format_where(self.where)
        else:
            s += '\n\n(no where)' 
        s += '\n' + indent(self.warning.format_user(), ' > ')
        return s


def warnings_copy_from_child_make_nested2(context, context2, where, msg):
    for w in context2.warnings:
        if isinstance(w, MCDPNestedWarning) and w.where is None:
            w2 = MCDPNestedWarning(msg=msg, where=where, warning=w.warning)
            context.warnings.append(w2)
        else:
            context.warnings.append(w)


def warnings_copy_from_child_make_nested(context0, context, msg, where):
    assert context0 is not context
    for w in context.warnings:
        w2 = MCDPNestedWarning(msg=msg, where=where, warning=w)
        context0.warnings.append(w2)

def warnings_copy_from_child_add_filename(context0, context, filename):
    for w in context.warnings:
        w2 = w.copy_with_filename(filename)
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
