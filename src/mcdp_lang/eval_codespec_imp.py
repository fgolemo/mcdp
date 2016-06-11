from .parse_actions import add_where_information
from .parts import CDPLanguage
from .utils_lists import unwrap_list
from conf_tools import instantiate_spec
from conf_tools.exceptions import ConfToolsException
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
        _args, kwargs = eval_arguments(r.arguments)
    else:
        kwargs = {}
    check_isinstance(function, str)

    with add_where_information(r.where):
        try:
            res = instantiate_spec([function, kwargs])
        except ConfToolsException as e:
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
    # n=3 is given as:
    # List2(e0=ArgName(value='n', where=Where('n')),
    # e1=ValueExpr(value=3, where=Where('3')), where=Where('n=3'))]

    ops = unwrap_list(arguments)
    n = len(ops)
    assert n % 2 == 0
    res = {}
    for i in range(n / 2):
        assert isinstance(ops[i], CDP.ArgName)
        assert isinstance(ops[i + 1], CDP.ValueExpr)
        k = ops[i].value
        v = ops[i + 1].value
        res[k] = v
    return (), res
