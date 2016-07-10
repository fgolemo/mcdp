# -*- coding: utf-8 -*-
from .parse_actions import add_where_information
from .parts import CDPLanguage
from contracts import contract
from contracts.utils import raise_desc
from mcdp_dp import PrimitiveDP
from mcdp_lang.namedtuple_tricks import recursive_print
from mocdp.exceptions import DPInternalError


CDP = CDPLanguage

@contract(returns=PrimitiveDP)
def eval_primitivedp(r, context):  # @UnusedVariable
    with add_where_information(r.where):
        if isinstance(r, CDP.LoadDP):
            # XXX: use Context to do it
            name = r.name.value
            return context.load_primitivedp(name)

        if isinstance(r, (CDP.CodeSpecNoArgs, CDP.CodeSpec)):
            return eval_primitivedp_code_spec(r, context)
        
        assert not isinstance(r, CDP.CodeSpec)

    r = recursive_print(r)
    msg = 'eval_primitivedp(): cannot evaluate r as a PrimitiveDP.'
    raise_desc(DPInternalError, msg, r=r)

def eval_primitivedp_code_spec(r, context):  # @UnusedVariable
    from .eval_codespec_imp import eval_codespec
    res = eval_codespec(r, expect=PrimitiveDP)
    return res

