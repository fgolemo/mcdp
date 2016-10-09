# -*- coding: utf-8 -*-
from .eval_codespec_imp_utils import InstantiationException, instantiate_spec
from .parse_actions import add_where_information
from .parts import CDPLanguage
from .utils_lists import unwrap_list
from contracts import contract
from contracts.utils import check_isinstance, raise_wrapped
from mocdp.exceptions import DPSemanticError

CDP = CDPLanguage

__all__ = [
    'eval_codespec',
]

def eval_codespec(r, expect):
    assert isinstance(r, (CDP.CodeSpecNoArgs, CDP.CodeSpec))

    function = r.function.value

    if isinstance(r, CDP.CodeSpec):
        print r.arguments
        _args, kwargs = eval_arguments(r.arguments)
    else:
        kwargs = {}
    check_isinstance(function, str)

    with add_where_information(r.where):
        try:
            res = instantiate_spec([function, kwargs])
        except InstantiationException as e:
            msg = 'Could not instantiate code spec.'
            raise_wrapped(DPSemanticError, e, msg, compact=True,
                          function=function, kwargs=kwargs)

        try:
            check_isinstance(res, expect)
        except ValueError as e:
            msg = 'The code did not return the correct type.'
            raise_wrapped(DPSemanticError, e, msg, r=r, res=res, expect=expect)

        return res


@contract(returns='tuple(tuple, dict)')
def eval_arguments(arguments):
# List2(e0=ArgName(value='element', where=Where('element')), e1=ArgValue(python_value="'*'", where=Where("'*'")), where=Where
# ("element='*'"))
    ops = unwrap_list(arguments)
    n = len(ops)
    assert n % 2 == 0
    res = {}
    for i in range(n / 2):
        o1 = ops[i * 2]
        o2 = ops[i * 2 + 1]
        assert isinstance(o1, CDP.ArgName)
        assert isinstance(o2, CDP.ArgValue)
        k = o1.value
        v = o2.python_value
        res[k] = v
    return (), res
