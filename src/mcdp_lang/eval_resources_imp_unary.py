# -*- coding: utf-8 -*-
from abc import abstractmethod, ABCMeta

from contracts import contract
from contracts.utils import raise_desc, check_isinstance, raise_wrapped, indent
from mcdp_dp import (CeilDP, SqrtRDP,
    SquareNatDP, SquareDP)
from mcdp_dp.conversion import get_conversion
from mcdp_dp.dp_max import MinF1DP, MinR1DP, JoinNDP, MaxF1DP, MaxR1DP, MeetNDP, JoinNDualDP, \
    MeetNDualDP
from mcdp_dp.dp_misc_unary import CeilToNatDP, Floor0DP
from mcdp_lang.eval_constant_imp import eval_constant, NotConstant
from .helpers import get_valuewithunits_as_resource, get_valuewithunits_as_function, create_operation_lf
from .utils_lists import unwrap_list
from mcdp_posets import Nat, Rcomp, RcompUnits
from mcdp_posets import NotLeq, get_types_universe
from mocdp.comp.context import ValueWithUnits
from mocdp.exceptions import DPSemanticError

from .helpers import create_operation
from .parts import CDPLanguage


CDP = CDPLanguage

 
class RuleInterface():
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_arguments_type(self):
        """ 
            Returns a tuple of OpSpec.
             
        """
        raise NotImplementedError
    
    @abstractmethod
    def apply(self, symbols, resources_or_constants, are_they_constant, context):
        """ Returns an Rvalue """
    
class RuleFloorDisallowed(RuleInterface):
    """ Floor is not Scott continuous """
    def get_arguments_type(self):
        msg = ('In contrast to ceil(), floor() is not Scott-continuous, '
               'so it cannot be used on resources (on this side of the equality). '
               'There is a function availabled called floor0(), which is equal '
               'to floor() everywhere, except at integers, where floor0(x) = x-1.')
        class Warn(OpSpecInterface):
            def applies(self, rtype, is_constant, symbols):  # @UnusedVariable
                raise DPSemanticError(msg)
        spec = Warn()
        return (spec,)
    
    def apply(self, _symbols, resources_or_constants, are_they_constant, context):
        # this will never get executed
        pass # pragma: no cover
    
    

class OneRGiveMeADP(RuleInterface):
    
    @abstractmethod
    def generate_dp(self, R):
        """ """
    
    def apply(self, symbols, resources_or_constants, are_they_constant, context):  # @UnusedVariable
        assert len(resources_or_constants) == 1
        is_constant = are_they_constant[0]
    
        if is_constant:
            R = resources_or_constants[0].unit
        else:
            R = context.get_rtype(resources_or_constants[0])
        
        dp = self.generate_dp(R)
            
        if is_constant:
            amap = dp.amap
            value = resources_or_constants[0].cast_value(amap.get_domain())
            result = amap(value)
            vu = ValueWithUnits(result, amap.get_codomain())
            return get_valuewithunits_as_resource(vu, context)
        else:
            r = resources_or_constants[0]
            return create_operation(context, dp, [r], name_prefix='_sqrt')
        
        
class RuleCeilRcomp(OneRGiveMeADP):
    """ ceil: Rcomp -> Nat"""
    
    def get_arguments_type(self):
        spec = OpSpecCastable(Rcomp())
        return (spec,)

    def generate_dp(self, R):  # @UnusedVariable
        return CeilToNatDP(Rcomp(), Nat())
        

class RuleCeilRcompUnits(OneRGiveMeADP):
    """ ceil: Joules -> Joules """
    
    def get_arguments_type(self):
        return (OpSpecIsinstance(RcompUnits),)

    def generate_dp(self, R):  # @UnusedVariable
        return CeilDP(R, R)
        
    

    
class RuleSQRTRcompUnits(OneRGiveMeADP):
    """ ceil: Joules -> Joules """
    
    def get_arguments_type(self):
        return (OpSpecIsinstance(RcompUnits),)

    def generate_dp(self, R):
        return SqrtRDP(R)


class RuleSQRTRcomp(OneRGiveMeADP):
    """ ceil: R -> R"""
    
    def get_arguments_type(self):
        return (OpSpecExactly(Rcomp()),)

    def generate_dp(self, _):
        return SqrtRDP(Rcomp())
      


    
class RuleFloor0RcompUnits(OneRGiveMeADP):
    """ ceil: Joules -> Joules """
    
    def get_arguments_type(self):
        return (OpSpecIsinstance(RcompUnits),)

    def generate_dp(self, R):
        return Floor0DP(R)
    
class RuleFloor0Rcomp(OneRGiveMeADP):
    """ ceil: R -> R"""
    
    def get_arguments_type(self):
        return (OpSpecExactly(Rcomp()),)

    def generate_dp(self, _):
        return Floor0DP(Rcomp())
      
class RuleSQRTRcompCastable(OneRGiveMeADP):
    """ ceil: R -> R"""
    
    def get_arguments_type(self):
        return (OpSpecCastable(Rcomp()),)

    def generate_dp(self, _):
        return SqrtRDP(Rcomp())
      

    
class RuleSquareNat(OneRGiveMeADP):
    """ ceil: Joules -> Joules """
    
    def get_arguments_type(self):
        spec = OpSpecExactly(Nat())
        return (spec,)

    def generate_dp(self, R):  # @UnusedVariable
        return SquareNatDP()


class RuleSquareRcomp(OneRGiveMeADP):
    """ ceil: Joules -> Joules """
    
    def get_arguments_type(self):
        spec = OpSpecExactly(Rcomp())
        return (spec,)

    def generate_dp(self, R):  # @UnusedVariable
        return SquareDP(Rcomp())

class RuleSquareRcompunits(OneRGiveMeADP):
    """ ceil: Joules -> Joules """
    def get_arguments_type(self):
        spec = OpSpecIsinstance(RcompUnits)
        return (spec,)

    def generate_dp(self, R):
        return SquareDP(R)

    
class OpSpecDoesntMatch(Exception):
    pass

class OpSpecInterface():
    
    @abstractmethod
    def applies(self, rtype, is_constant, symbols):
        """ Raises OpSpecDoesntMatch """ 
    
class OpSpecTrue(OpSpecInterface):
    def applies(self, rtype, is_constant, symbols):
        pass


class OpSpecExactly(OpSpecInterface):
    def __init__(self, P):
        self.P = P
    def applies(self, rtype, is_constant, symbols):  # @UnusedVariable
        tu = get_types_universe()
        if not tu.equal(rtype, self.P):
            msg = 'Poset %s does not match %s.' % (rtype, self.P)
            raise OpSpecDoesntMatch(msg)

class OpSpecIsinstance(OpSpecInterface):
    def __init__(self, X):
        self.X = X
        
    def applies(self, P, is_constant, symbols):  # @UnusedVariable
        try: 
            check_isinstance(P, self.X)
        except ValueError:
            msg = 'Poset %s does not match %s.' % (P, self.X)
            raise_desc(OpSpecDoesntMatch, msg)
        
class OpSpecCastable(OpSpecInterface):
    def __init__(self, castable_to):
        self.castable_to = castable_to
        
    def applies(self, P, _is_constant, _symbols):
        try:
            get_conversion(self.castable_to, P) # XXX: will have to invert this
        except NotLeq:
            msg = 'Could not find a conversion from %s to %s.' % (P, self.castable_to)
            raise_desc(OpSpecDoesntMatch, msg)
        

class OpSpecMarkSymbol(OpSpecInterface):
    
    @contract(symbol='str', other=OpSpecInterface)
    def __init__(self, symbol, other):
        self.symbol = symbol
        self.other = other
        
    def applies(self, rtype, is_constant, symbols):
        # needs to match
        self.other.applies(rtype, is_constant, symbols)
        
        if self.symbol in symbols:
            R0 = symbols[self.symbol] 
            try:
                get_conversion(R0, rtype) # XXX: will have to invert this
            except NotLeq:
                msg = 'Could not convert %s to %s.' % (rtype, R0) 
                raise_desc(OpSpecDoesntMatch, msg)
        else:
            symbols[self.symbol] = rtype
             
        
class AssociativeOp(RuleInterface):
    
    @abstractmethod
    def only_one(self, constant):
        """ """

    @abstractmethod
    def reduce_constants(self, vus):
        """ constants: list of ValueWithUnits """
        
    @abstractmethod
    def return_op_constant(self, context, resource, vu):
        """ """
    
    @abstractmethod
    def return_op_variables(self, context, resources):
        """ """
         
    def apply(self, symbols, resources_or_constants, are_they_constant, context):  # @UnusedVariable
        """ Returns an Rvalue """
        
        # Find out how many are constants
        constants = []
        resources = []
        for x, is_constant in zip(resources_or_constants, are_they_constant):
            if is_constant:
                constants.append(x)
            else:
                resources.append(x)
        
        # it's a constant value
        if len(resources) == 0:
            vu = self.reduce_constants(constants)
            return self.only_one(vu, context)
            
        # it's only resource * (c1*c2*c3*...)
        if len(resources) == 1:
            vu = self.reduce_constants(constants)
            res = self.return_op_constant(context, resources[0], vu=vu)
            assert res is not None
            return res
        else:
            r = self.return_op_variables(context, resources)
            assert r is not None
            if not constants:
                return r
            else:
                vu = self.reduce_constants(constants)
                return self.return_op_constant(context, r, vu)
                
        assert False

class AssociativeOpRes(AssociativeOp):
    def only_one(self, vu, context):
        return get_valuewithunits_as_resource(vu, context)

class AssociativeOpFun(AssociativeOp):
    def only_one(self, vu, context):
        return get_valuewithunits_as_function(vu, context)

class OpJoin(AssociativeOpRes):
    """
        r >= max(f1, f2)
    """
    def __init__(self, nargs):
        assert nargs >= 2    
        self.nargs = nargs
    
    def get_arguments_type(self):
        spec = OpSpecMarkSymbol('A', OpSpecTrue()) 
        return (spec,) * self.nargs

    def reduce_constants(self, vus):
        S = vus[0].unit
        res = vus[0].value
        for _ in vus[1:]:
            v = _.cast_value(S)
            res = S.join(res, v)
        return ValueWithUnits(res, S)
            
    def return_op_constant(self, context, resource, vu):
        check_isinstance(vu, ValueWithUnits)
        dp = MaxF1DP(vu.unit, vu.value) 
        return create_operation(context, dp, [resource], name_prefix='_max1a')

    def return_op_variables(self, context, resources):
        F = context.get_rtype(resources[0])
        dp = JoinNDP(len(resources), F)
        return create_operation(context, dp, resources, name_prefix='_maxn')


class OpJoinFun(AssociativeOpRes):
    
    """ max(r, 2) >= f """
    
    def __init__(self, nargs):
        assert nargs >= 2    
        self.nargs = nargs
    
    def get_arguments_type(self):
        spec = OpSpecMarkSymbol('A', OpSpecTrue()) 
        return (spec,) * self.nargs

    def reduce_constants(self, vus):
        S = vus[0].unit
        res = vus[0].value
        for _ in vus[1:]:
            v = _.cast_value(S)
            res = S.join(res, v)
        return ValueWithUnits(res, S)
            
    def return_op_constant(self, context, function, vu):
        check_isinstance(vu, ValueWithUnits)
        dp = MaxR1DP(vu.unit, vu.value) 
        return create_operation_lf(context, dp, [function], name_prefix='_max1a')

    def return_op_variables(self, context, functions):
        F = context.get_ftype(functions[0])
        dp = JoinNDualDP(len(functions), F)
        return create_operation_lf(context, dp, functions, name_prefix='_maxf_n')


class OpMeetFun(AssociativeOpFun):
    
    """ min(r, 2) >= f """
    def __init__(self, nargs):
        assert nargs >= 2    
        self.nargs = nargs
    
    def get_arguments_type(self):
        spec = OpSpecMarkSymbol('A', OpSpecTrue()) 
        return (spec,) * self.nargs

    def reduce_constants(self, vus):
        S = vus[0].unit
        res = vus[0].value
        for _ in vus[1:]:
            v = _.cast_value(S)
            res = S.meet(res, v)
        return ValueWithUnits(res, S)
            
    def return_op_constant(self, context, function, vu):
        check_isinstance(vu, ValueWithUnits)
        dp = MinR1DP(vu.unit, vu.value) 
        return create_operation_lf(context, dp, [function], name_prefix='_max1a')

    def return_op_variables(self, context, functions):
        F = context.get_ftype(functions[0])
        dp = MeetNDualDP(len(functions), F)
        return create_operation_lf(context, dp, functions, name_prefix='_meetf_n')

class OpMeet(AssociativeOpRes):
    
    def __init__(self, nargs):
        assert nargs >= 2    
        self.nargs = nargs
    
    def get_arguments_type(self):
        spec = OpSpecMarkSymbol('A', OpSpecTrue()) 
        return (spec,) * self.nargs

    def reduce_constants(self, vus):
        S = vus[0].unit
        res = vus[0].value
        for _ in vus[1:]:
            v = _.cast_value(S)
            res = S.meet(res, v)
        return ValueWithUnits(res, S)
            
    def return_op_constant(self, context, resource, vu):
        check_isinstance(vu, ValueWithUnits)
        dp = MinF1DP(vu.unit, vu.value) 
        return create_operation(context, dp, [resource], name_prefix='_min1a')

    def return_op_variables(self, context, resources):
        F = context.get_rtype(resources[0])
        dp = MeetNDP(len(resources), F)
        return create_operation(context, dp, resources, name_prefix='_minn')

generic_op_fun = []
generic_op_res = []
for nargs in range(2, 8):
    generic_op_res.append(('op_res_max_%d' % nargs, 'max', OpJoin(nargs)))
    generic_op_res.append(('op_res_min_%d' % nargs, 'min', OpMeet(nargs)))
    generic_op_fun.append(('op_fun_max_%d' % nargs, 'max', OpJoinFun(nargs)))
    generic_op_fun.append(('op_fun_min_%d' % nargs, 'min', OpMeetFun(nargs)))

generic_op_res.append(('op_res_ceil_rcompunits', 'ceil', RuleCeilRcompUnits()))
generic_op_res.append(('op_res_ceil_rcomp',  'ceil', RuleCeilRcomp()))

generic_op_res.append(('op_res_floor', 'floor', RuleFloorDisallowed()))
generic_op_res.append(('op_res_floor0_rcomp', 'floor0', RuleFloor0Rcomp()))
generic_op_res.append(('op_res_floor0_rcomp', 'floor0', RuleFloor0RcompUnits()))

generic_op_res.append(('op_res_sqrt_rcompunits', 'sqrt', RuleSQRTRcompUnits()))
generic_op_res.append(('op_res_sqrt_rcomp', 'sqrt', RuleSQRTRcomp()))
generic_op_res.append(('op_res_sqrt_rcomp_cast', 'sqrt', RuleSQRTRcompCastable()))

generic_op_res.append(('op_res_square_nat', 'square', RuleSquareNat()))
generic_op_res.append(('op_res_square_rcomp', 'square', RuleSquareRcomp())) 
generic_op_res.append(('op_res_square_rcompunits', 'square', RuleSquareRcompunits())) 


def get_best_match(opname, rtypes, are_they_constant, generic_ops):
    """ Raises NotMatching """
    check_isinstance(opname, str)
    assert len(rtypes) == len(are_they_constant)
    
    names_available = set(name for _,name,_ in generic_ops)
    if not opname in names_available:
        msg = 'Unknown operation %r.' % opname
        msg += ' Available: ' + ", ".join(sorted(names_available)) + '.'
        raise_desc(NotMatching, msg)
        
        
    problems = []
    for (id_op, name, op) in generic_ops:
        if name != opname:
            continue
        try: 
            symbols = match_op(op, rtypes, are_they_constant)
        except NotMatching as e:
            problems.append((id_op, e))
            continue
        except DPSemanticError as e:
            # for now, warning about floor() not being scott-continuous
            raise
        return op, symbols
    
        
    msg = ('Could not find a match with any of the %d version(s) of %r.' % 
           (len(problems), opname))
    ops = []    
    for R, is_constant in zip(rtypes, are_they_constant):
        o = 'constant %s' % R if is_constant else '%s' % R
        ops.append(o)
    proto = "%s(%s)" % (opname, ", ".join(ops))
    msg += '\n' + 'I was looking for a prototype like:\n\n    %s' % proto
    msg += '\n\nHowever, I got these problems:\n'
    for id_op, e in problems:
        prefix = '   ' + id_op + ':'
        msg += '\n' + indent(' ' + str(e).strip(), ' ' * len(prefix), first=prefix)
    raise_desc(NotMatching, msg)
        
class NotMatching(Exception):
    pass

def match_op(op, rtypes, are_they_constant):
    """ Returns symbols or raises NotMatching """
    requires = op.get_arguments_type()
    if len(requires) != len(rtypes):
        msg = 'Wrong number of args (expected %d, found %d).' % (len(requires), len(rtypes))
        raise_desc(NotMatching, msg)
        
    symbols = {}
    for i, (spec, R, is_constant) in \
        enumerate(zip(requires, rtypes, are_they_constant)):
        try:
            spec.applies(R, is_constant, symbols)
        except OpSpecDoesntMatch as e:
            raise_desc(NotMatching, str(e).strip())
    return symbols

def sort_resources_and_constants(ops, mode, context):
    """ 
        Returns a tuple of three arrays:
            types, are_they_constant, resources_or_constants
        
        mode is either 'functions' or 'resources'
        
        resources_or_constants contains either CResources or ValueWithUnits
    """
    assert mode in ['functions', 'resources']
    
    rtypes = []
    are_they_constant = []
    resources_or_constants = []
    for op in ops:
        try:
            c = eval_constant(op, context)
            resources_or_constants.append(c)
            rtypes.append(c.unit)
            are_they_constant.append(True)
            continue
        except NotConstant:
            pass

        if mode == 'resources':
            from .eval_resources_imp import eval_rvalue
            ref = eval_rvalue(op, context)
            P = context.get_rtype(ref)
        elif mode == 'functions':
            from .eval_lfunction_imp import eval_lfunction
            ref = eval_lfunction(op, context)
            P = context.get_ftype(ref)
        else:
            assert False
            
        resources_or_constants.append(ref)
        are_they_constant.append(False)
        rtypes.append(P)
    return rtypes, are_they_constant, resources_or_constants


def eval_rvalue_generic_operation(r, context):
    assert isinstance(r, CDP.GenericOperationRes)
    opname = r.name.value
    ops = unwrap_list(r.ops)
    
    rtypes, are_they_constant, resources_or_constants = \
        sort_resources_and_constants(ops, 'resources', context)
        
    try:
        op, symbols = get_best_match(opname, rtypes, are_they_constant,
                                     generic_op_res)
    except NotMatching as e:
        raise_desc(DPSemanticError, str(e).strip())
    r = op.apply(symbols, resources_or_constants, are_they_constant, context)
    return r

def eval_lfunction_genericoperationfun(r, context):
    assert isinstance(r, CDP.GenericOperationFun)
    opname = r.name.value
    ops = unwrap_list(r.ops)
    
    rtypes, are_they_constant, resources_or_constants = \
        sort_resources_and_constants(ops, 'functions', context)
        
    try:
        op, symbols = get_best_match(opname, rtypes, are_they_constant,
                                     generic_op_fun)
    except NotMatching as e:
        msg = 'Could not find any operation that matches.'
        raise_wrapped(DPSemanticError, e, msg, opname=opname, rtypes=rtypes,
                      are_they_constant=are_they_constant)
    
    lf = op.apply(symbols, resources_or_constants, are_they_constant, context)
    return lf
