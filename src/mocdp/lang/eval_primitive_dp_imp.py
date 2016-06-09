# -*- coding: utf-8 -*-
from .eval_codespec_imp import eval_codespec
from .parts import CDPLanguage
from conf_tools import SemanticMistakeKeyNotFound
from contracts import contract
from contracts.utils import check_isinstance, raise_wrapped
from mocdp.configuration import get_conftools_dps
from mocdp.dp import PrimitiveDP
from mocdp.exceptions import DPInternalError, DPSemanticError


CDP = CDPLanguage


@contract(returns=PrimitiveDP)
def eval_pdp(r, context):  # @UnusedVariable
    try:
        if isinstance(r, CDP.LoadDP):
            name = r.name.value
            try:
                _, dp = get_conftools_dps().instance_smarter(name)
            except SemanticMistakeKeyNotFound as e:
                raise DPSemanticError(str(e), r.where)

            return dp

        if isinstance(r, (CDP.CodeSpecNoArgs, CDP.CodeSpec)):
            res = eval_codespec(r)

            try:
                check_isinstance(res, PrimitiveDP)
            except ValueError as e:
                msg = 'Expected the code to give a subclass of PrimitiveDP.'
                raise_wrapped(DPSemanticError, e, msg, r=r)
            return res
    except DPSemanticError as e:
        if e.where is None:
            raise DPSemanticError(str(e), where=r.where)
        
    raise DPInternalError('Invalid pdp rvalue: %s' % str(r))

