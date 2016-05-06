from mocdp.lang.tests.utils import parse_wrap_check
from mocdp.lang.syntax import Syntax
from comptests.registrar import comptest
from mocdp.lang.parse_actions import parse_ndp
from mocdp.posets.uppersets import UpperSets

@comptest
def check_coproducts0():
    parse_wrap_check('a ^ b', Syntax.ndpt_dp_rvalue)


@comptest
def check_coproducts1():
    parse_wrap_check('choose(a:a, b:b)', Syntax.ndpt_dp_rvalue)


    s = """
        mcdp {
            provides energy [J]
            requires budget [$]
            
            a = mcdp {
                provides energy [J]
                requires budget [$]
                budget >= 5 $
                energy <= 10 J
            }
            
            b = mcdp {
                provides energy [J]
                requires budget [$]
                budget >= 5 $
                energy <= 50 J
            }
            
            c = instance choose(optionA:a, optionB:b)
            energy <= c.energy
            budget >= c.budget
        }    
    """
    ndp = parse_ndp(s)
    dp = ndp.get_dp()
    R = dp.get_res_space()
    I = dp.get_imp_space()
    print('R: %s' % R)
    print('I: %s' % I)
    UR = UpperSets(R)
    res = dp.solve(0.0)
    print UR.format(res)

    imps = dp.get_implementations_f_r(f=0.0, r=R.get_top())
    print imps



