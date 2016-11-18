# -*- coding: utf-8 -*-
import functools
import math

from contracts import contract
from contracts.utils import check_isinstance, raise_wrapped, raise_desc
from mocdp import ATTRIBUTE_NDP_RECURSIVE_NAME
from mocdp.exceptions import DPSyntaxError, do_extra_checks, mcdp_dev_warning
from mocdp.memoize_simple_imp import memoize_simple
from pint import UnitRegistry  # @UnresolvedImport
from pint.errors import UndefinedUnitError  # @UnresolvedImport

from .any import Any, BottomCompletion, TopCompletion
from .poset import is_top, is_bottom
from .rcomp import RcompBase, Rbicomp
from .space import Map


class MyUnitRegistry(UnitRegistry):
    def __init__(self, *args, **kwargs):
        UnitRegistry.__init__(self, *args, **kwargs)
        self.define(' dollars = [cost] = USD')
        self.define(' flops = [flops]')
        self.define(' pixels = [pixels]')
        self.define(' episodes = [episodes]')
        self.define(' CHF = 1.03 dollars')
        self.define(' EUR = 1.14 dollars')

_ureg = MyUnitRegistry()


def get_ureg():
    ureg = _ureg
    return ureg

class RcompUnits(RcompBase):

    def __init__(self, pint_unit, string):
        if do_extra_checks():
            ureg = get_ureg()
            check_isinstance(pint_unit, ureg.Quantity)
            
        RcompBase.__init__(self)
        self.units = pint_unit
        self.string = string
        u = parse_pint(string)
        # assert u == self.units, (self.units, u, string)
        assert str(u) == str(self.units), (self.units, u, string)

        self.units_formatted = format_pint_unit_short(self.units)

    @memoize_simple
    def __repr__(self):
        # need to call it to make sure dollars is defined
        ureg = get_ureg()  # @UnusedVariable

        # graphviz does not support three-byte unicode
        # c = "ℝ̅"
        # c = "ℝᶜ"
        c = 'R'

        if self.units == R_dimensionless.units:
            return '%s[]' % c

        return "%s[%s]" % (c, self.units_formatted)

    def __copy__(self):
        other = RcompUnits(self.units, self.string)
        return other

    def __getstate__(self):
        # print('__getstate__  %s %s' % (id(self), self.__dict__))

        # See: https://github.com/hgrecco/pint/issues/349
        # This is a hack

        state = {
            'top': self.top,
            'string': self.string,
            'units_formatted': self.units_formatted,
        }

        att = ATTRIBUTE_NDP_RECURSIVE_NAME
        if hasattr(self, att):
            state[att] = getattr(self, att)
        return state

    def __setstate__(self, x):
        # print('__setstate__ %s %r' % (id(self), x))
        self.top = x['top']
        self.string = x['string']
        self.units = parse_pint(self.string)
        self.units_formatted = x['units_formatted']

        att = ATTRIBUTE_NDP_RECURSIVE_NAME
        if att in x:
            setattr(self, att, x[att])

    def __eq__(self, other):
        if isinstance(other, RcompUnits):
            eq = (other.units == self.units)
            return eq
        return False

    def format(self, x):
        if x == self.top:
            s = self.top.__repr__()
        else:
            s = RcompBase.format(self, x)

        if self.units_formatted:
            return '%s %s' % (s, self.units_formatted)
        else:
            return s

mcdp_dev_warning('(!) Need to create plenty of checks for this Rbicomb.')

class RbicompUnits(Rbicomp):
    """ [-inf, inf] """

    def __init__(self, pint_unit, string):
        if do_extra_checks():
            ureg = get_ureg()
            check_isinstance(pint_unit, ureg.Quantity)

        Rbicomp.__init__(self)
        self.units = pint_unit
        self.string = string
        u = parse_pint(string)
        assert u == self.units, (self.units, u, string)

        self.units_formatted = format_pint_unit_short(self.units)
    
    @staticmethod
    def from_rcompunits(P):
        check_isinstance(P, RcompUnits)
        return RbicompUnits(pint_unit=P.units, string=P.string)

    @memoize_simple
    def __repr__(self):
        # need to call it to make sure dollars is defined
        ureg = get_ureg()  # @UnusedVariable

        # graphviz does not support three-byte unicode
        # c = "ℝ̅"
        # c = "ℝᶜ"
        c = 'Rbi'

        if self.units == R_dimensionless.units:
            return '%s[]' % c

        return "%s[%s]" % (c, self.units_formatted)

    def __copy__(self):
        other = RbicompUnits(self.units, self.string)
        return other

    def __getstate__(self):
        # print('__getstate__  %s %s' % (id(self), self.__dict__))

        # See: https://github.com/hgrecco/pint/issues/349
        # This is a hack

        state = {
            'top': self.top,
            'bottom': self.bottom,
            'string': self.string,
            'units_formatted': self.units_formatted,
        }

        if hasattr(self, ATTRIBUTE_NDP_RECURSIVE_NAME):
            state[ATTRIBUTE_NDP_RECURSIVE_NAME] = \
                getattr(self, ATTRIBUTE_NDP_RECURSIVE_NAME)
        return state

    def __setstate__(self, x):
        # print('__setstate__ %s %r' % (id(self), x))
        self.top = x['top']
        self.bottom = x['bottom']
        self.string = x['string']
        self.units = parse_pint(self.string)
        self.units_formatted = x['units_formatted']

        if ATTRIBUTE_NDP_RECURSIVE_NAME in x:
            setattr(self, ATTRIBUTE_NDP_RECURSIVE_NAME, 
                    x[ATTRIBUTE_NDP_RECURSIVE_NAME])

    def __eq__(self, other):
        if isinstance(other, RbicompUnits):
            eq = (other.units == self.units)
            return eq
        return False

    def format(self, x):
        if x == self.top:
            s = self.top.__repr__()
        elif x == self.bottom:
            s = self.bottom.__repr__()
        else:
            s = Rbicomp.format(self, x)

        if self.units_formatted:
            return '%s %s' % (s, self.units_formatted)
        else:
            return s


@memoize_simple
def parse_pint(s0):
    """ thin wrapper taking care of dollars not recognized """
    s = s0.replace('$', ' dollars ')
    ureg = get_ureg()
    try:
        return ureg.parse_expression(s)

    except (UndefinedUnitError, SyntaxError) as e:
        msg = 'Cannot parse units %r.' % s0
        raise_wrapped(DPSyntaxError, e, msg, compact=True)
        # ? for some reason compact does not have effect here
    except Exception as e:
        msg = 'Cannot parse units %r (%s).' % (s0, type(e))
        raise_wrapped(DPSyntaxError, e, msg)

# @memoize_simple
# cannot use memoize because we use setattr later
def make_rcompunit(units):
    try:
        s = units.strip()
    
        mcdp_dev_warning('obsolete?')
        if s.startswith('set of'):
            t = s.split('set of')
            u = make_rcompunit(t[1])
            from mcdp_posets import FiniteCollectionsInclusion
            return FiniteCollectionsInclusion(u)

        mcdp_dev_warning('obsolete?')
        if s == 'any':
            return BottomCompletion(TopCompletion(Any()))
    
        if s == 'R':
            raise DPSyntaxError('Form R is not recognized anymore. Use "dimensionless".')
        
            s = 'm/m'
        unit = parse_pint(s)
    except DPSyntaxError as e:
        msg = 'Cannot parse %r.' % units
        raise_wrapped(DPSyntaxError, e, msg)
        
    return RcompUnits(unit, s)

R_Power_units = parse_pint('W')
R_Energy_units = parse_pint('J')
R_Weight_units = parse_pint('kg')
R_Weight_g_units = parse_pint('g')
R_Force_units = parse_pint('N')

def format_pint_unit_short(units):
    # some preferred ways
    if units == R_Power_units:  # units = A*V*s
        return 'W'
    if units == R_Energy_units:
        return 'J'
    if units == R_Weight_units:
        return 'kg'
    if units == R_Weight_g_units:
        return 'g'
    if units == R_Force_units:
        return 'N'

    x = '{:~}'.format(units)
    x = x.replace('1.0', '')
    if not '/' in x:
        x = x.replace('1', '')  # otherwise 1 / s -> / s
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
R_Energy_J = make_rcompunit('J')
R_Weight = make_rcompunit('kg')
R_Weight_g = make_rcompunit('g')

R_Current = make_rcompunit('A')
R_Voltage = make_rcompunit('V')


def mult_table_seq(seq):
    return functools.reduce(mult_table, seq)

@contract(a=RcompUnits, b=RcompUnits)
def mult_table(a, b):
    check_isinstance(a, RcompUnits)
    check_isinstance(b, RcompUnits)

    unit2 = a.units * b.units
    s = '%s' % unit2
    return RcompUnits(unit2, s)

def check_mult_units_consistency_seq(factors, c):
    for f in factors:
        check_isinstance(f, RcompUnits)
    check_isinstance(c, RcompUnits)
    c_expected = mult_table_seq(factors)
    if c.units != c_expected.units:
        msg = 'For the multiplication of %s  I expected %s but got %s' % (factors, c_expected, c)
        raise_desc(AssertionError, msg)


def check_mult_units_consistency(a, b, c):
    """ Checks that a * b = c and raises AssertionError if not. """
    check_isinstance(a, RcompUnits)
    check_isinstance(b, RcompUnits)
    check_isinstance(c, RcompUnits)
    c_expected = mult_table(a, b)
    if c.units != c_expected.units:
        msg = 'For %s x %s I expected %s but got %s' % (a, b, c_expected, c)
        raise_desc(AssertionError, msg)


@contract(a=RcompUnits)
def inverse_of_unit(a):
    check_isinstance(a, RcompUnits)
    unit2 = 1 / a.units
    s = '%s' % unit2
    return RcompUnits(unit2, s)

def RbicompUnits_reflect(P, x):
    check_isinstance(P, RbicompUnits)
    if is_top(P, x):
        return P.get_bottom()
    if is_bottom(P, x):
        return P.get_top()
    return -x
    
class UndefinedRbicompUnitsResult(Exception):
    pass

def RbicompUnits_subtract(P, x, y):
    """
        Raises UndefinedRbicompUnitsResult
    """
    # computes x-y in P
    check_isinstance(P, RbicompUnits)
    y2 = RbicompUnits_reflect(P, y)
    try:
        return RbicompUnits_add(P, x, y2)
    except UndefinedRbicompUnitsResult as e:
        msg = 'Could not subtract.'
        raise_desc(UndefinedRbicompUnitsResult, e, msg)


def RbicompUnits_add(P, x, y):
    """
        Raises UndefinedRbicompUnitsResult
    """
    def undefined():
        msg = 'Undefined addition.'
        raise_desc(UndefinedRbicompUnitsResult, msg, x=P.format(x), y=P.format(y))
        
    if is_top(P, x):
        if is_top(P, y):
            return P.get_top()
        elif is_bottom(P, y):
            return undefined() 
        return P.get_top()
    elif is_bottom(P, x):
        if is_top(P, y):
            return undefined() 
        elif is_bottom(P, y):
            return P.get_bottom() 
        return P.get_bottom()
    else:
        # x is normal: 
        if is_top(P, y):
            return undefined() 
        elif is_bottom(P, y):
            return P.get_bottom()
        mcdp_dev_warning('underflow, overflow')
        return x + y 
    
def rcomp_add(x, y):
    from .rcomp import Rcomp
    P = Rcomp()
    x_is_top = is_top(P, x)
    y_is_top = is_top(P, y)
    
    if x_is_top or y_is_top:
        return P.get_top()
    mcdp_dev_warning('underflow, overflow')    
    return x + y

def rcompunits_add(P, x, y):
    check_isinstance(P, RcompUnits)
    x_is_top = is_top(P, x)
    y_is_top = is_top(P, y)
    
    if x_is_top or y_is_top:
        return P.get_top()
    mcdp_dev_warning('underflow, overflow')    
    return x + y


@contract(a=RcompUnits, num='int', den='int')
def rcompunits_pow(a, num, den):
    """
        Gets the unit for a ^ (num/den)
    """
    check_isinstance(a, RcompUnits)
    x = 1.0 * num / den
    u = a.units ** x
    s = '%s' % u
    return RcompUnits(u, s)


class RCompUnitsPowerMap(Map):
    """ 
        Computes:
         
            x |-> x ^ (num/den)
    """

    def __init__(self, F, num, den):
        R = rcompunits_pow(F, num, den)
        Map.__init__(self, dom=F, cod=R)
        self.num = num
        self.den = den

    def _call(self, x):
        if self.dom.equal(x, self.dom.get_top()):
            return self.cod.get_top()
        e = 1.0 * self.num / self.den
        try:
            r = math.pow(x, e)
            return r
        except OverflowError:
            return self.cod.get_top()

    def __repr__(self): # XXX
        s = '^ '
        s += '%d' % self.num
        if self.den != 1:
            s += '/%s' % self.den
        return s
    
    def repr_map(self, letter):
        return '%s ⟼ %s ^ %s/%s ' % (letter, letter, self.num, self.den)

        
