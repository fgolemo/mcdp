# -*- coding: utf-8 -*-

from .parts import CDPLanguage
from conf_tools import SemanticMistakeKeyNotFound
from contracts import contract
from contracts.utils import check_isinstance, raise_wrapped, raise_desc
from mocdp.configuration import get_conftools_dps
from mocdp.dp import PrimitiveDP
from mocdp.exceptions import DPInternalError, DPSemanticError
from mcdp_lang.parse_actions import add_where_information


CDP = CDPLanguage

@contract(returns=PrimitiveDP)
def eval_primitivedp(r, context):  # @UnusedVariable
    with add_where_information(r.where):
        if isinstance(r, CDP.LoadDP):
            name = r.name.value
            try:
                _, dp = get_conftools_dps().instance_smarter(name)
            except SemanticMistakeKeyNotFound as e:
                raise DPSemanticError(str(e), r.where)

            return dp


        if isinstance(r, (CDP.CodeSpecNoArgs, CDP.CodeSpec)):
            return eval_primitivedp_code_spec(r, context)
        
        assert not isinstance(r, CDP.CodeSpec)
    raise_desc(DPInternalError, 'Invalid primitivedp expression', r=r)

def eval_primitivedp_code_spec(r, context):  # @UnusedVariable
    from .eval_codespec_imp import eval_codespec
    res = eval_codespec(r, expect=PrimitiveDP)
    return res

