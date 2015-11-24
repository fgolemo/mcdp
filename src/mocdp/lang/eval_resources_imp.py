# -*- coding: utf-8 -*-
from .parts import CDPLanguage
from contracts import contract, raise_wrapped
from contracts.utils import raise_desc
from mocdp.comp import Connection, dpwrap
from mocdp.comp.context import CResource, ValueWithUnits
from mocdp.dp import GenericUnary, Max, Max1, Min, WrapAMap
from mocdp.exceptions import DPInternalError, DPSemanticError
from mocdp.posets import Map, Nat, NotBelongs, Rcomp, RcompUnits
from mocdp.posets.rcomp_units import RCompUnitsPower
import numpy as np




CDP = CDPLanguage
class DoesNotEvalToResource(Exception):
    """ also called "rvalue" """

@contract(returns=CResource)
def eval_rvalue(rvalue, context):
    """
        raises DoesNotEvalToResource
    """
    # wants Resource or NewFunction
    try:
        if isinstance(rvalue, CDP.Divide):
            from mocdp.lang.eval_math import eval_divide_as_rvalue
            return eval_divide_as_rvalue(rvalue, context)

        if isinstance(rvalue, CDP.Resource):
            return context.make_resource(dp=rvalue.dp.value, s=rvalue.s.value)

        if isinstance(rvalue, CDP.NewFunction):
            fname = rvalue.name
            try:
                dummy_ndp = context.get_ndp_fun(fname)
            except ValueError as e:
                msg = 'New resource name %r not declared.' % fname
                msg += '\n%s' % str(e)
                raise DPSemanticError(msg, where=rvalue.where)

            return context.make_resource(context.get_name_for_fun_node(fname),
                            dummy_ndp.get_rnames()[0])

        def eval_ops(rvalue):
            """ Returns a, F1, b, F2 """
            a = eval_rvalue(rvalue.a, context)
            b = eval_rvalue(rvalue.b, context)
            F1 = context.get_rtype(a)
            F2 = context.get_rtype(b)
            return a, F1, b, F2

        def add_binary(dp, nprefix, na, nb, nres):
            nres = context.new_res_name(nres)
            na = context.new_fun_name(na)
            nb = context.new_fun_name(nb)

            ndp = dpwrap(dp, [na, nb], nres)
            name = context.new_name(nprefix)
            c1 = Connection(dp1=a.dp, s1=a.s, dp2=name, s2=na)
            c2 = Connection(dp1=b.dp, s1=b.s, dp2=name, s2=nb)
            context.add_ndp(name, ndp)
            context.add_connection(c1)
            context.add_connection(c2)
            return context.make_resource(name, nres)

        if isinstance(rvalue, CDP.MultN):
            from mocdp.lang.eval_math import eval_MultN_as_rvalue
            return eval_MultN_as_rvalue(rvalue, context)

        if isinstance(rvalue, CDP.PlusN):
            from mocdp.lang.eval_math import eval_PlusN_as_rvalue
            return eval_PlusN_as_rvalue(rvalue, context)

        if isinstance(rvalue, CDP.OpMax):

            if isinstance(rvalue.a, CDP.SimpleValue):
                b = eval_rvalue(rvalue.b, context)
                # print('a is constant')
                name = context.new_name('max1')
                ndp = dpwrap(Max1(rvalue.a.unit, rvalue.a.value), '_in', '_out')
                context.add_ndp(name, ndp)
                c = Connection(dp1=b.dp, s1=b.s, dp2=name, s2='_in')
                context.add_connection(c)
                return context.make_resource(name, '_out')

            a = eval_rvalue(rvalue.a, context)

            if isinstance(rvalue.b, CDP.SimpleValue):
                name = context.new_name('max1')
                ndp = dpwrap(Max1(rvalue.b.unit.value, rvalue.b.value.value), '_in', '_out')
                context.add_ndp(name, ndp)
                c = Connection(dp1=a.dp, s1=a.s, dp2=name, s2='_in')
                context.add_connection(c)
                return context.make_resource(name, '_out')

            b = eval_rvalue(rvalue.b, context)

            F1 = context.get_rtype(a)
            F2 = context.get_rtype(b)

            if not (F1 == F2):
                msg = 'Incompatible units for Max(): %s and %s' % (F1, F2)
                msg += '%s and %s' % (type(F1), type(F2))
                raise DPSemanticError(msg, where=rvalue.where)

            dp = Max(F1)
            nprefix, na, nb, nres = 'opmax', 'm0', 'm1', 'max'

            return add_binary(dp, nprefix, na, nb, nres)

        if isinstance(rvalue, CDP.OpMin):
            a, F1, b, F2 = eval_ops(rvalue)
            if not (F1 == F2):
                msg = 'Incompatible units: %s and %s' % (F1, F2)
                raise DPSemanticError(msg, where=rvalue.where)

            dp = Min(F1)
            nprefix, na, nb, nres = 'opmin', 'm0', 'm1', 'min'

            return add_binary(dp, nprefix, na, nb, nres)

        if isinstance(rvalue, CDP.SimpleValue):
            # implicit conversion from int to float
            unit = rvalue.unit.value
            value = rvalue.value.value
            # XXX: stuff here
            if isinstance(unit, Rcomp):
                if isinstance(value, int):
                    value = float(value)
            try:
                unit.belongs(value)
            except NotBelongs as e:
                raise_wrapped(DPSemanticError, e, "Value is not in the give space.")

            c = ValueWithUnits(value, unit)
            from mocdp.lang.helpers import get_valuewithunits_as_resource
            return get_valuewithunits_as_resource(c, context)

        if isinstance(rvalue, CDP.VariableRef):
            if rvalue.name in context.constants:
                return eval_rvalue(context.constants[rvalue.name], context)

            elif rvalue.name in context.var2resource:
                return context.var2resource[rvalue.name]

            try:
                dummy_ndp = context.get_ndp_fun(rvalue.name)
            except ValueError as e:
                msg = 'New function name %r not declared.' % rvalue.name
                msg += '\n%s' % str(e)
                raise DPSemanticError(msg, where=rvalue.where)

            s = dummy_ndp.get_rnames()[0]
            return context.make_resource(context.get_name_for_fun_node(rvalue.name), s)

        if isinstance(rvalue, CDP.GenericNonlinearity):
            op_r = eval_rvalue(rvalue.op1, context)
            # this is supposed to be a numpy function that takes a scalar float
            function = rvalue.function
            # R_from_F = rvalue.R_from_F TODO: remove
            F = context.get_rtype(op_r)
            
            # tu = get_types_universe()
            if isinstance(F, Rcomp) or isinstance(F, RcompUnits):
                R = F
                dp = GenericUnary(F=F, R=R, function=function)
            elif isinstance(F, Nat):
                m = CeilAfter(function, dom=Nat(), cod=Nat())
                dp = WrapAMap(m)
            else:
                msg = 'Cannot create unary operator'
                raise_desc(DPInternalError, msg, function=function, F=F)

            fnames = context.new_fun_name('s')
            name = context.new_name(function.__name__)
            rname = context.new_res_name('res')

            ndp = dpwrap(dp, fnames, rname)
            context.add_ndp(name, ndp)

            c = Connection(dp1=op_r.dp, s1=op_r.s, dp2=name, s2=fnames)

            context.add_connection(c)

            return context.make_resource(name, rname)

        if isinstance(rvalue, CDP.Power):
            base = eval_rvalue(rvalue.op1, context)
            exponent = rvalue.exponent

            if isinstance(exponent, CDP.IntegerFraction):
                num = exponent.num
                den = exponent.den
            elif isinstance(exponent, int):
                num = exponent
                den = 1
            else:
                assert False

            print('base: %s expo %d %d' % (base, num, den))
            print('base: %s' % context.get_rtype(base))
            
            F = context.get_rtype(base)
            m = RCompUnitsPower(F, num=num, den=den)
            print('m: %s' % m)

            raise NotImplementedError()

        msg = 'Cannot evaluate as resource.'
        raise_desc(DoesNotEvalToResource, msg, rvalue=rvalue)
    except DPSemanticError as e:
        if e.where is None:
            raise DPSemanticError(str(e), where=rvalue.where)
        raise e

class CeilAfter(Map):
    """ Applies a function and rounds it to int. """

    def __init__(self, f, dom, cod):
        self.f = f
        Map.__init__(self, dom, cod)

    def _call(self, x):
        if np.isinf(x):
            return self.cod.get_top()
        
        y = self.f(x * 1.0)
        if np.isinf(y):
            return self.cod.get_top()
        
        y = int(np.ceil(y))
        return y




