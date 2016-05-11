# -*- coding: utf-8 -*-
from .parts import CDPLanguage
from conf_tools import SemanticMistakeKeyNotFound, instantiate_spec
from conf_tools.exceptions import ConfToolsException
from contracts import contract
from contracts.utils import check_isinstance, raise_wrapped
from mocdp.configuration import get_conftools_dps
from mocdp.dp.primitive import PrimitiveDP
from mocdp.exceptions import DPInternalError, DPSemanticError
from mocdp.lang.utils_lists import unwrap_list

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

        if isinstance(r, (CDP.PDPCodeSpecNoArgs, CDP.PDPCodeSpec)):
            function = r.function.value
            
            if isinstance(r, CDP.PDPCodeSpec):
                _args, kwargs = eval_arguments(r.arguments)
            else:
                kwargs = {}
            check_isinstance(function, str)
            try:
                res = instantiate_spec([function, kwargs])
            except ConfToolsException as e:
                msg = 'Could not instantiate code spec.'
                raise_wrapped(DPSemanticError, e, msg, compact=True,
                              function=function, kwargs=kwargs)
            try:
                check_isinstance(res, PrimitiveDP)
            except ValueError as e:
                msg = 'Expected the code to give a subclass of PrimitiveDP.'
                raise_wrapped(DPSemanticError, e, msg, function=function,
                              kwargs=kwargs)
            return res
    except DPSemanticError as e:
        if e.where is None:
            raise DPSemanticError(str(e), where=r.where)
        
    raise DPInternalError('Invalid pdp rvalue: %s' % str(r))

@contract(returns='tuple(tuple, dict)')
def eval_arguments(arguments):
    # n=3 is given as:
    # List2(e0=ArgName(value='n', where=Where('n')),
    # e1=ValueExpr(value=3, where=Where('3')), where=Where('n=3'))]

    ops = unwrap_list(arguments)
    n = len(ops)
    assert n % 2 == 0
    res = {}
    for i in range(n/2):
        assert isinstance(ops[i], CDP.ArgName)
        assert isinstance(ops[i + 1], CDP.ValueExpr)
        k = ops[i].value
        v = ops[i + 1].value
        res[k] = v
    return (), res
