# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc
from mcdp_dp import PrimitiveDP
from mcdp_lang.parse_actions import decorate_add_where
from mcdp.exceptions import DPInternalError

from .namedtuple_tricks import recursive_print
from .parts import CDPLanguage


CDP = CDPLanguage

@decorate_add_where
@contract(returns=PrimitiveDP)
def eval_primitivedp(r, context):  # @UnusedVariable
    if isinstance(r, CDP.LoadDP):
        name = r.name.value
        return context.load_primitivedp(name)

    if isinstance(r, (CDP.CodeSpecNoArgs, CDP.CodeSpec)):
        return eval_primitivedp_code_spec(r, context)
    
    if True: # pragma: no cover
        r = recursive_print(r)
        msg = 'eval_primitivedp(): cannot evaluate r as a PrimitiveDP.'
        raise_desc(DPInternalError, msg, r=r)

def eval_primitivedp_code_spec(r, context):  # @UnusedVariable
    assert isinstance(r, (CDP.CodeSpecNoArgs, CDP.CodeSpec))
    from .eval_codespec_imp import eval_codespec
    res = eval_codespec(r, expect=PrimitiveDP)
    return res

