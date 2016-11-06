# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, check_isinstance, raise_wrapped
from mcdp_dp import (Floor0DP, CeilDP, CeilSqrtNatDP, SqrtRDP,
    SquareNatDP, SquareDP)
from mcdp_dp import PrimitiveDP
from mcdp_dp.dp_identity import IdentityDP
from mcdp_posets import Map, Nat, Rcomp, RcompUnits
from mocdp import logger
from mocdp.comp.context import CResource, ValueWithUnits
from mocdp.exceptions import DPSemanticError

from .helpers import get_resource_possibly_converted, create_operation
from .parts import CDPLanguage
from mcdp_dp.dp_misc_unary import CeilToNatDP
from mcdp_posets.rcomp_units import R_dimensionless
from mcdp_lang.utils_lists import unwrap_list
from mcdp_posets.poset import Poset, NotLeq
from mcdp_dp.conversion import get_conversion
from mcdp_lang.eval_constant_imp import eval_constant, NotConstant
from mcdp_lang.eval_resources_imp import eval_rvalue
from mcdp_lang.helpers import get_valuewithunits_as_resource,\
    get_valuewithunits_as_function
from abc import abstractmethod, ABCMeta
from mcdp_dp.dp_max import Max1, JoinNDP, Min1, MeetNDP


CDP = CDPLanguage

class Rule():
    def __init__(self, opname, test_type, cast_type_to, use_map, warn=None):
        self.opname = opname
        self.test_type = test_type
        self.cast_type_to = cast_type_to
        self.use_map = use_map
        self.warn = warn
        
   
        
    def applies(self, opname, F):
        if self.opname != opname:
            return False
        
        if not self.test_type(F):
            return False
        else:
            return True
    
    @contract(op_r=CResource)
    def build(self, op_r, context):
        if self.warn:
            logger.warn(self.warn)
        F = context.get_rtype(op_r)
        if self.cast_type_to is not None:
            op_r = get_resource_possibly_converted(op_r, F, context)
            F = self.cast_type_to
            
        amap = self.use_map(F)
        if isinstance(amap, Map):
            raise Exception(amap)
        else:
            assert isinstance(amap, PrimitiveDP)
            dp = amap
            
        return create_operation(context, dp, [op_r],
                                         name_prefix='_%s'% self.opname, 
                                         op_prefix='_in',
                                         res_prefix='_out')
            



def get_unary_rules():
     
    # note that RcompUnits derives from Rcomp so we must have this check
    def is_RcompUnits(T):
        return isinstance(T, RcompUnits)
    
    def is_Rcomp(T):
        return isinstance(T, Rcomp)

    def is_RcompUnits_dimensionless(T):
        return isinstance(T, RcompUnits) and T.units == R_dimensionless.units
    
    def is_Nat(T):
        return isinstance(T, Nat)
        
    rules = [
        # sqrt(Nat): promote to Rcomp()
        # sqrt(Rcomp)
        # sqrt(Rcomp)
        Rule('sqrt', is_Nat, Rcomp(), lambda _: SqrtRDP(Rcomp())), # XXX
        Rule('sqrt', is_Rcomp, None,  lambda _: SqrtRDP(Rcomp())),
        Rule('sqrt', is_RcompUnits, None,  lambda F: SqrtRDP(F)),
             
        # square: Nat -> Nat
        # square: Rcomp -> Rcomp
        # square: Rcompunits -> Rcompunits
        Rule('square', is_Nat, None, lambda _: SquareNatDP()), 
        Rule('square', is_Rcomp, None, lambda F: SquareDP(F)), 
        Rule('square', is_RcompUnits, None, lambda F: SquareDP(F)), 

        Rule('ceilsqrt', is_Nat, None, lambda _: CeilSqrtNatDP()), 

        Rule('ceil', is_Nat, None, lambda _: IdentityDP(Nat(), Nat()), warn='ceil() used on Nats'), 
        Rule('ceil',lambda x: is_Rcomp(x) or is_RcompUnits_dimensionless(x), 
                    None, 
                    lambda _: CeilToNatDP(Rcomp(), Nat())), 
        
        Rule('ceil', is_RcompUnits, None, lambda F: CeilDP(F)),
        
        Rule('floor', is_Nat, None, lambda _: IdentityDP(Nat(), Nat()), warn='floor() used on Nats'), 
        Rule('floor', is_Rcomp, None, lambda _: Floor0DP(Rcomp())), 
        Rule('floor', is_RcompUnits, None, lambda F: Floor0DP(F)),
    ]
    return rules

unary_rules = get_unary_rules()


ANY_POSET = 'ANY_POSET'

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
        pass
    
class OpSpec():
    def __init__(self, poset, must_be_constant, assign_symbol):
        if not poset == ANY_POSET:
            check_isinstance(poset, Poset)
            
        if poset == ANY_POSET:
            assert assign_symbol is not None
            
        self.poset = poset
        self.must_be_constant = must_be_constant
        self.assign_symbol = assign_symbol
        
class AssociativeOp(RuleInterface):
    
    @abstractmethod
    def only_one(self, constant):
        pass

    @abstractmethod
    def reduce_constants(self, vus):
        """ constants: list of ValueWithUnits """
        
    @abstractmethod
    def return_op_constant(self, context, resource, vu):
        pass
    
    @abstractmethod
    def return_op_variables(self, context, resources):
        pass
         
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
    
    def __init__(self, nargs):
        assert nargs >= 2    
        self.nargs = nargs
    
    def get_arguments_type(self):
        spec = OpSpec(poset=ANY_POSET, must_be_constant=False, assign_symbol='A') 
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
        dp = Max1(vu.unit, vu.value) 
        return create_operation(context, dp, [resource], name_prefix='_max1a')

    def return_op_variables(self, context, resources):
        F = context.get_rtype(resources[0])
        dp = JoinNDP(len(resources), F)
        return create_operation(context, dp, resources, name_prefix='_maxn')

class OpMeet(AssociativeOp):
    
    def __init__(self, nargs):
        assert nargs >= 2    
        self.nargs = nargs
    
    def get_arguments_type(self):
        spec = OpSpec(poset=ANY_POSET, must_be_constant=False, assign_symbol='A') 
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
        dp = Min1(vu.unit, vu.value) 
        return create_operation(context, dp, [resource], name_prefix='_min1a')

    def return_op_variables(self, context, resources):
        F = context.get_rtype(resources[0])
        dp = MeetNDP(len(resources), F)
        return create_operation(context, dp, resources, name_prefix='_minn')

generic_ops = []
for nargs in range(2, 8):
    generic_ops.append(('max', OpJoin(nargs)))
    generic_ops.append(('min', OpMeet(nargs)))

def get_best_match(opname, rtypes, are_they_constant):
    check_isinstance(opname, str)
    assert len(rtypes) == len(are_they_constant)
    
    for (name, op) in generic_ops:
        if name != opname:
            continue
        
        try: 
            symbols = match_op(op, rtypes, are_they_constant)
        except NotMatching as e:
            #print e
            continue
    
        return op, symbols
    
    msg = 'Did not match with anything.'
    raise_desc(NotMatching, msg, rtypes=rtypes, 
               are_they_constant=are_they_constant)
        
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
        
        if spec.must_be_constant and not is_constant:
            msg = 'Expect argument %d to be constant.' % i
            raise_desc(NotMatching, msg)
        
        if spec.poset == ANY_POSET:
            if spec.assign_symbol is not None:
                if spec.assign_symbol in symbols:
                    must_be_castable_to = symbols[spec.assign_symbol]
                else:
                    must_be_castable_to = None
            else:
                must_be_castable_to = None
        else:
            must_be_castable_to = spec.poset
            
        if must_be_castable_to is not None:
            # check R can be cast to must_be_castable_to
            try:
                get_conversion(must_be_castable_to, R) # XXX: will have to invert this
            except NotLeq as e:
                msg = 'Could not match %s to %s' % (R, must_be_castable_to)
                raise_wrapped(NotMatching, e, msg, exc=sys.exc_info())
            
        if spec.assign_symbol is not None and not spec.assign_symbol in symbols:
            symbols[spec.assign_symbol] = R
            
    return symbols

import sys

def eval_rvalue_generic_operation(r, context):
    assert isinstance(r, CDP.GenericOperationRes)
    opname = r.name.value
    ops = unwrap_list(r.ops)
    
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
        except NotConstant as e:
            pass

        r = eval_rvalue(op, context)
        resources_or_constants.append(r)
        are_they_constant.append(False)
        rtypes.append(context.get_rtype(r))
    
    try:
        op, symbols = get_best_match(opname, rtypes, are_they_constant)
    except NotMatching as e:
        msg = 'Could not find any operation that matches.'
        raise_wrapped(DPSemanticError, e, msg, opname=opname, rtypes=rtypes,
                      are_they_constant=are_they_constant)
    
    r = op.apply(symbols, resources_or_constants, are_they_constant, context)
    return r


def eval_rvalue_unary(r, context):
    """ This is supposed to be a numpy function that takes a scalar float.
        The rvalue must have type Rcomp or Rcompunits.
    """
    from .eval_resources_imp import eval_rvalue

    assert isinstance(r, CDP.UnaryRvalue)
    proc = r.proc 
    assert isinstance(proc, CDP.ProcName)
    op_r = eval_rvalue(r.rvalue, context)
    F = context.get_rtype(op_r)
    
    for rule in unary_rules:
        if rule.applies(proc.name, F):
            return rule.build(op_r, context)
    
    msg = ('Cannot create unary operator %r for %s.'% (proc.name, F))
    raise_desc(DPSemanticError, msg, F=F)
    