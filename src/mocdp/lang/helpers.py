# -*- coding: utf-8 -*-
from .parse_actions import plus_constantsN
from .parts import CDPLanguage
from conf_tools import (ConfToolsException, SemanticMistakeKeyNotFound,
    instantiate_spec)
from contracts import contract, describe_value
from contracts.utils import check_isinstance, indent, raise_desc, raise_wrapped
from mocdp.comp import (CompositeNamedDP, Connection, NamedDP, NotConnected,
    SimpleWrap, dpwrap)
from mocdp.comp.context import CFunction, CResource, ValueWithUnits, \
    NoSuchMCDPType
from mocdp.configuration import get_conftools_dps, get_conftools_nameddps
from mocdp.dp import (
    Constant, GenericUnary, Identity, InvMult2, InvPlus2, Limit, Max, Max1, Min,
    PrimitiveDP, ProductN, SumN)
from mocdp.dp.dp_catalogue import CatalogueDP
from mocdp.dp.dp_generic_unary import WrapAMap
from mocdp.dp.dp_series_simplification import make_series
from mocdp.exceptions import DPInternalError, DPSemanticError
from mocdp.lang.parse_actions import inv_constant
from mocdp.posets import (NotBelongs, NotEqual, NotLeq, PosetProduct, Rcomp,
    Space, get_types_universe, mult_table, mult_table_seq)
from mocdp.posets.any import Any
from mocdp.posets.finite_set import FiniteCollection, FiniteCollectionsInclusion
from mocdp.posets.nat import Nat

def square(x):
    res = x * x
    return res



@contract(resources='seq')
def create_operation(context, dp, resources, name_prefix, op_prefix, res_prefix):
    name = context.new_name(name_prefix)
    name_result = context.new_res_name(res_prefix)

    connections = []
    fnames = []
    for i, r in enumerate(resources):
        ni = context.new_fun_name('%s%s' % (op_prefix, i))
        c = Connection(dp1=r.dp, s1=r.s, dp2=name, s2=ni)
        fnames.append(ni)
        connections.append(c)

    if len(fnames) == 1:
        fnames = fnames[0]

    ndp = dpwrap(dp, fnames, name_result)
    context.add_ndp(name, ndp)

    for c in connections:
        context.add_connection(c)

    res = context.make_resource(name, name_result)
    return res


@contract(v=ValueWithUnits)
def get_valuewithunits_as_resource(v, context):
    dp = Constant(R=v.unit, value=v.value)
    nres = context.new_res_name('c')
    ndp = dpwrap(dp, [], nres)
    context.add_ndp(nres, ndp)
    return context.make_resource(nres, nres)



def get_conversion(A, B):
    """ Returns None if there is no need. """
    tu = get_types_universe()
    try:
        tu.check_leq(A, B)
    except NotLeq as e:
        msg = 'Wrapping with incompatible units.'
        raise_wrapped(DPSemanticError, e, msg, A=A, B=B)

    if tu.equal(A, B):
        conversion = None
    else:
        A_to_B, _ = tu.get_embedding(A, B)
        conversion = WrapAMap(A_to_B)

    return conversion
