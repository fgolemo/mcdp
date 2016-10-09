from comptests.registrar import comptest
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_lang.parse_interface import parse_ndp
from mcdp_lang.syntax import Syntax
from .utils import parse_wrap_check
from mocdp.exceptions import DPSemanticError, DPSyntaxError


@comptest
def check_approx_res1():
    s = 'approx(provided f, 10 g)'
    parse_wrap_check(s, Syntax.rvalue_approx_step)
    parse_wrap_check(s, Syntax.rvalue)
    
@comptest
def check_approx_res2():
    s = """
        mcdp {
            requires y [m]
            
            provides x [m]
            
            y >= approx(x, 1 cm)
        }
    """
    ndp = parse_ndp(s)
    dp = ndp.get_dp()
    res = dp.solve(0.006)
    assert res.minimals == set([0.01])
    res = dp.solve(0.016)
    assert res.minimals == set([0.02])

@comptest
def check_approx_res3():
    s = """
        mcdp {
            requires y [m]
            
            provides x [m]
            
            y >= approx(x, 1 J)
        }
    """
    try:
        parse_ndp(s)
    except DPSemanticError as e:
        s = str(e)
        assert 'The step is specified in a unit' in s
    else:
        raise Exception()


@comptest
def check_approx_res4(): # check_error line
    s = ("""
    
    
    mcdp {
        provides f [m]
        requires r [m]
        
        
        r >= f
        r >= f
        r >= f
        r >= f
        r >= f
        r >= f
        r >= f
        r >= f
        r >= f
        r >= f f
    
    """)
    try:
        parse_ndp(s)  # , Syntax.ndpt_dp_rvalue)
    except DPSyntaxError as e:
        s = str(e)
        assert  'line 18' in s
        return
    else:
        raise Exception()
#     parse_wrap_check(s, Syntax.ndpt_dp_operand)
    # parse_wrap_check(s, Syntax.ndpt_dp_model)

@comptest
def check_approx_res5():
    s = """
        mcdp {
            requires y [m]
            
            provides x [m]
            
            y >= approxu(x, 1 cm)
        }
    """
    ndp = parse_ndp(s)
    dp = ndp.get_dp()
    dpl, dpu = get_dp_bounds(dp, 1, 1)
    resl = dpl.solve(0.016)
    resu = dpu.solve(0.016)
    print resl
    print resu
    assert resl.minimals == set([0.01])
    assert resu.minimals == set([0.02])


@comptest
def check_approx_res6():
    pass


@comptest
def check_approx_res7():
    pass


@comptest
def check_approx_res8():
    pass


@comptest
def check_approx_res9():
    pass

