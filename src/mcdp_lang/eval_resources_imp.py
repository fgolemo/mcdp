# -*- coding: utf-8 -*-
from .eval_constant_imp import eval_constant
from .helpers import get_valuewithunits_as_resource
from .parse_actions import add_where_information
from .parts import CDPLanguage
from contracts import contract
from contracts.utils import raise_desc
from mocdp.comp.context import CResource, ValueWithUnits, get_name_for_fun_node
from mocdp.exceptions import DPSemanticError


CDP = CDPLanguage

class DoesNotEvalToResource(DPSemanticError):
    """ also called "rvalue" """

@contract(returns=CResource)
def eval_rvalue(rvalue, context):
    """
        raises DoesNotEvalToResource
    """
    assert not isinstance(rvalue, ValueWithUnits)
    # wants Resource or NewFunction
    with add_where_information(rvalue.where):

        constants = (CDP.Collection, CDP.SimpleValue, CDP.SpaceCustomValue,
                     CDP.Top, CDP.Bottom)
        if isinstance(rvalue, constants):
            res = eval_constant(rvalue, context)
            assert isinstance(res, ValueWithUnits)
            return get_valuewithunits_as_resource(res, context)

#         try:
#             res = eval_constant(rvalue, context)  # should we clone the context?
#             assert isinstance(res, ValueWithUnits)
#             return get_valuewithunits_as_resource(res, context)
#         except NotConstant:
#             pass

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

            return context.make_resource(get_name_for_fun_node(fname),
                                         dummy_ndp.get_rnames()[0])



        if isinstance(rvalue, CDP.VariableRef):
            if rvalue.name in context.constants:
                c = context.constants[rvalue.name]
                assert isinstance(c, ValueWithUnits)
                return get_valuewithunits_as_resource(c, context)
                # return eval_rvalue(context.constants[rvalue.name], context)

            elif rvalue.name in context.var2resource:
                return context.var2resource[rvalue.name]

            try:
                dummy_ndp = context.get_ndp_fun(rvalue.name)
            except ValueError as e:
                msg = 'New function name %r not declared.' % rvalue.name
                msg += '\n%s' % str(e)
                raise DPSemanticError(msg, where=rvalue.where)

            s = dummy_ndp.get_rnames()[0]
            return context.make_resource(get_name_for_fun_node(rvalue.name), s)


        from .eval_resources_imp_power import eval_Power
        from .eval_math import eval_divide_as_rvalue
        from .eval_math import eval_MultN_as_rvalue
        from .eval_math import eval_PlusN_as_rvalue
        from .eval_resources_imp_minmax import eval_OpMax
        from .eval_resources_imp_minmax import eval_OpMin
        from .eval_resources_imp_genericnonlin import eval_GenericNonlinearity
        from .eval_resources_imp_tupleindex import eval_TupleIndex_as_rvalue
        from .eval_resources_imp_maketuple import eval_MakeTuple_as_rvalue

        cases = {
            CDP.GenericNonlinearity : eval_GenericNonlinearity,
            CDP.Power: eval_Power,
            CDP.Divide: eval_divide_as_rvalue,
            CDP.MultN: eval_MultN_as_rvalue,
            CDP.PlusN: eval_PlusN_as_rvalue,
            CDP.OpMax: eval_OpMax,
            CDP.OpMin: eval_OpMin,
            CDP.TupleIndex: eval_TupleIndex_as_rvalue,
            CDP.MakeTuple: eval_MakeTuple_as_rvalue,
        }

        for klass, hook in cases.items():
            if isinstance(rvalue, klass):
                return hook(rvalue, context)

        msg = 'Cannot evaluate as resource.'
        raise_desc(DoesNotEvalToResource, msg, rvalue=rvalue)

