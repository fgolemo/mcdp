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

CDP = CDPLanguage
@contract(returns=PrimitiveDP)
def eval_pdp(r, context):  # @UnusedVariable
    if isinstance(r, CDP.LoadDP):
        name = r.name.value
        try:
            _, dp = get_conftools_dps().instance_smarter(name)
        except SemanticMistakeKeyNotFound as e:
            raise DPSemanticError(str(e), r.where)

        return dp

    if isinstance(r, CDP.PDPCodeSpec):
        function = r.function.value
        arguments = r.arguments
        check_isinstance(function, str)
        res = instantiate_spec([function, arguments])
        return res

    raise DPInternalError('Invalid pdp rvalue: %s' % str(r))
