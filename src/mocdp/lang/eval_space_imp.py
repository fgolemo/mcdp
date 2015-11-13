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
from mocdp.lang.utils_lists import get_odd_ops, unwrap_list
CDP = CDPLanguage

@contract(returns=Space)
def eval_space(r, context):
    if isinstance(r, CDP.PowerSet):
        P = eval_space(r.space, context)
        return FiniteCollectionsInclusion(P)
    if isinstance(r, CDP.Nat):
        return Nat()
    if isinstance(r, CDP.SpaceProduct):
        ops = get_odd_ops(unwrap_list(r.ops))
        Ss = [eval_space(_, context) for _ in ops]
        return PosetProduct(tuple(Ss))
    if isinstance(r, CDP.Unit):
        return r.value
    raise DPInternalError('Invalid value to eval_space: %s' % str(r))


@contract(returns=Space)
def eval_unit(x, context):  # @UnusedVariable

    if isinstance(x, CDP.Unit):
        S = x.value
        assert isinstance(S, Space), S
        return S

    msg = 'Cannot evaluate %s as unit.' % x.__repr__()
    raise ValueError(msg)
