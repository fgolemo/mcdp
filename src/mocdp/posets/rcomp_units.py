# -*- coding: utf-8 -*-
from .any import Any, BottomCompletion, TopCompletion
from .rcomp import Rcomp
from contracts.utils import check_isinstance, raise_wrapped
from mocdp.exceptions import DPSyntaxError
from pint import UnitRegistry
from pint.unit import UndefinedUnitError
import functools
from contracts import contract


class MyUnitRegistry(UnitRegistry):
    def __init__(self, *args, **kwargs):
        UnitRegistry.__init__(self, *args, **kwargs)
        self.define(' dollars = [cost]')
_ureg = MyUnitRegistry()


def get_ureg():
    ureg = _ureg
    return ureg

class RcompUnits(Rcomp):

    def __init__(self, pint_unit):
        ureg = get_ureg()
        check_isinstance(pint_unit, ureg.Quantity)
            
        Rcomp.__init__(self)
        self.units = pint_unit

    def __repr__(self):
        # need to call it to make sure dollars i defined
        ureg = get_ureg()  # @UnusedVariable

        if self.units == R_dimensionless.units:
            return 'R[]'
        return "R[%s]" % format_pint_unit_short(self.units)

    def __getstate__(self):
        # See: https://github.com/hgrecco/pint/issues/349
        u = self.units
        # This is a hack
        units_ex = (u.magnitude, u.units._units)
        # Original was:
        # units_ex = (u.magnitude, u.units)
        state = {'top': self.top, 'units_ex': units_ex}
        return state

    def __setstate__(self, x):
        self.top = x['top']
        units_ex = x['units_ex']
        ureg = get_ureg()
        self.units = ureg.Quantity(units_ex[0], units_ex[1])

    def __eq__(self, other):
        if isinstance(other, RcompUnits):
            eq = (other.units == self.units)
            return eq
        return False

    def format(self, x):
        if x == self.top:
            return self.top.__repr__()
        else:
            s = Rcomp.format(self, x)
            return '%s %s' % (s, format_pint_unit_short(self.units))


def parse_pint(s0):
    """ thin wrapper taking care of dollars not recognized """
    s = s0.replace('$', ' dollars ')
    ureg = get_ureg()
    try:
        return ureg.parse_expression(s)

    except (UndefinedUnitError, SyntaxError) as e:
        msg = 'Cannot parse units %r.' % s0
        raise_wrapped(DPSyntaxError, e, msg, compact=True)
    except Exception as e:
        msg = 'Cannot parse units %r.' % s0
        raise_wrapped(DPSyntaxError, e, msg)

def make_rcompunit(units):
    try:
        s = units.strip()
    
        if s.startswith('set of'):
            t = s.split('set of')
            u = make_rcompunit(t[1])
            from .finite_set import FiniteCollectionsInclusion
            return FiniteCollectionsInclusion(u)

        if s == 'any':
            return BottomCompletion(TopCompletion(Any()))
    
        if s == 'R':
            s = 'm/m'
        unit = parse_pint(s)
    except DPSyntaxError as e:
        msg = 'Cannot parse %r.' % units
        raise_wrapped(DPSyntaxError, e, msg)
    return RcompUnits(unit)

def format_pint_unit_short(units):
    # some preferred ways
    if units == R_Power.units:  # units = A*V*s
        return 'W'
    if units == R_Energy.units:
        return 'J'
    if units == R_Weight.units:
        return 'kg'
    if units == R_Weight_g.units:
        return 'g'
    if units == R_Force.units:
        return 'N'

    x = '{:~}'.format(units)
    x = x.replace('1.0', '')
    x = x.replace('1', '')
    x = x.replace('dollars', '$')
    x = x.replace(' ', '')
    x = x.replace('**', '^')
    x = x.replace('^2', '²')
    return str(x)

R_dimensionless = make_rcompunit('m/m')
R_Time = make_rcompunit('s')
R_Power = make_rcompunit('W')
R_Force = make_rcompunit('N')
R_Cost = make_rcompunit('$')
R_Energy = make_rcompunit('J')
R_Weight = make_rcompunit('kg')
R_Weight_g = make_rcompunit('g')

R_Current = make_rcompunit('A')
R_Voltage = make_rcompunit('V')


def mult_table_seq(seq):
    return functools.reduce(mult_table, seq)

@contract(a=RcompUnits, b=RcompUnits)
def mult_table(a, b):
    unit2 = a.units * b.units
    return RcompUnits(unit2)



