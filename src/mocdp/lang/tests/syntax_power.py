from .utils import ok, sem, syn
from mocdp.lang.parts import CDPLanguage
from mocdp.lang.syntax import Syntax

L = CDPLanguage


ok(Syntax.integer_fraction, '1/2', L.IntegerFraction(num=1, den=2))
syn(Syntax.integer_fraction, '1/2.0')
sem(Syntax.integer_fraction, '1/0')
syn(Syntax.integer_fraction, '1/')
ok(Syntax.power_expr, 'pow(x,1/2)',
    L.Power(op1=L.NewFunction('x'),  # XXX
            exponent=L.IntegerFraction(num=1, den=2)))
