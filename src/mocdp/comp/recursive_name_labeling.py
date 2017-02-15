# -*- coding: utf-8 -*-

"""

    Step 1:
    
    Each leaf NDP (i.e. SimpleWrap, not Composite or CoProduct)
     will be labeled with an attribute called 
    "ndp_recursive_name". This will be a tuple of strings.
    
    This is done by calling label_with_recursive_names(ndp).
    
    Step 2:
    
    Then, each time get_dp() is called, the attribute 
    is copied onto the PrimitiveDP generated.
    
    This is done in 3 places:
    - NamedDPCoproduct
    - CompositeNamedDP
    - SimpleWrap
    
    So now each DP has this attribute set.
    
    Note also this needs to be added to get_dp_bounds().
    
    Step 3:
    
    When get_imp_space() is called,
    the attribute is set on the imp space.
    
    Step 4:
    
    product_compact does not try to optimize a space if it has
    this attribute set.
    
    Step 5:
    
    cakk 
"""
from collections import namedtuple
from contracts import contract
from contracts.utils import raise_desc
from mcdp_dp import IdentityDP, Mux
from mcdp_posets import Coproduct1Labels, SpaceProduct
from mocdp.comp.composite import CompositeNamedDP, cndp_get_name_ndp_notfunres
from mocdp.comp.context import Context
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.labelers import LabelerNDP
from mocdp.comp.wrap import SimpleWrap
from mcdp.exceptions import DPInternalError, mcdp_dev_warning
from mocdp.ndp.named_coproduct import NamedDPCoproduct
from mcdp.constants import MCDPConstants

__all__ = [
    'get_labelled_version',
]


def get_labelled_version(ndp):
    return visit_hierarchy(ndp)

@contract(returns=NamedDP)
def visit_hierarchy(ndp0):
    """
        Visits the hierarchy in deep first.
    """

    def visit(recname, ndp):

        if isinstance(ndp, CompositeNamedDP):
            # NOTE: Does not label CompositeNamedDP
            context = Context()
            for child_name, child_ndp in ndp.get_name2ndp().items():
                child_ndp2 = visit(recname + (child_name,), child_ndp)
                context.add_ndp(child_name, child_ndp2)

            for c in ndp.get_connections():
                context.add_connection(c)
                
            context.fnames = ndp.get_fnames()
            context.rnames = ndp.get_rnames()
            res = CompositeNamedDP.from_context(context)
            return res

            # res2 = LabelerNDP(res, recname)
            # return res2

        elif isinstance(ndp, SimpleWrap):
            ndp2 = LabelerNDP(ndp, recname)
            return ndp2

        elif isinstance(ndp, NamedDPCoproduct):
            assert len(ndp.ndps) == len(ndp.labels), ndp
            children = []
            labels = []
            for child_ndp, child_label in zip(ndp.ndps, ndp.labels):
                child2 = visit(recname + (child_label,), child_ndp)
                children.append(child2)
                labels.append(child_label)
                
            res = NamedDPCoproduct(tuple(children), tuple(labels))
            res2 = LabelerNDP(res, recname)
            return res2
        elif isinstance(ndp, LabelerNDP):
            msg = 'Trying to re-label this as {}'.format(recname)
            raise_desc(DPInternalError, msg, ndp=ndp)
        else:
            raise NotImplementedError(type(ndp))

    return visit(recname=(), ndp=ndp0)

def get_names_used(I):
    """
        I = SpaceProduct, with some marked as ATTRIBUTE_NDP_RECURSIVE_NAME.
    
        Returns list of names or None.
    """
    att = MCDPConstants.ATTRIBUTE_NDP_RECURSIVE_NAME
    if hasattr(I, att):
        return [getattr(I, att)]
    
    if isinstance(I, SpaceProduct):
        res = []
        for sub in I.subs:
            if hasattr(sub, att):
                name = getattr(sub, att)
                assert isinstance(name, tuple)
                res.append(name)
            else:
                res.append(None)
        assert len(res) == len(I.subs)
        return res

    return []
        
@contract(returns=dict)
def collect(I, imp):
    I.belongs(imp)
    res = {}

    if isinstance(I, SpaceProduct):
        for j, sub in enumerate(I.subs):
            res.update(**collect(sub, imp[j]))

    elif isinstance(I, Coproduct1Labels):
        i, xi = I.unpack(imp)
        Ii = I.spaces[i]

        res.update(**collect(Ii, xi))
    else:
        pass
        
    mcdp_dev_warning('a little more thought')
    att = MCDPConstants.ATTRIBUTE_NDP_RECURSIVE_NAME
    if not res and hasattr(I, att):
        name = getattr(I, att)
        return {name: imp}

    return res


def get_imp_as_recursive_dict(I, imp):  # , ignore_hidden=True):
    """
        I = SpaceProduct, with some marked as ATTRIBUTE_NDP_RECURSIVE_NAME.
        
        imp = element of I
        
        returns a dictionary of dictionaries
        
        if ignore_hidden, we do not give the ones like _sum1, _invplus1, etc.
    """
    I.belongs(imp)
    res = collect(I, imp)

    # print('collected: %s' % res)

    if len(res) == 1 and list(res)[0] == ():
        return res[()]

    # now res has some keys that are tuples of length >= 0
    # res = {('a','b'): ., ('a','c'), ...}
    def group(res):
        res = dict(**res)
        # Let's call the top-level elements like 'a'
        tops = set()
        for key in list(res):
            if len(key) >= 2:
                tops.add(key[0])

            if len(key) == 1:
                res[key[0]] = res[key]
                del res[key]
        for top in list(tops):
            top_res = {}
            for k, v in list(res.items()):
                if len(k) >= 2 and k[0] == top:
                    del res[k]
                    top_res[k[1:]] = v
            res[top] = group(top_res)

        return res

    return group(res)

MakeArguments = namedtuple('MakeArguments', [
    'ndp',  # reference to CompositeNDP or SimpleWrap model
    'subresult',  # the result of the children
    'result',  # the result being built
    'key',  # the key for this make function
    'context',  # generic context
])

@contract(a=MakeArguments)
def make_identity(a):  # @UnusedVariable
    return a.subresult

def get_make_functions(ndp):
    att = MCDPConstants.ATTRIBUTE_NDP_MAKE_FUNCTION
    if hasattr(ndp, att):
        return getattr(ndp, att)
    else:
        return [ ('default', make_identity) ]

def ndp_make(ndp, imp_dict, context):
    """ A top-down make function.
    
        imp_dict = {name1: value, name2: value, ...}
        
    """
    if isinstance(ndp, CompositeNamedDP):
        children_artifact = {}
        for child_name, child in cndp_get_name_ndp_notfunres(ndp):
            if not child_name in imp_dict:
                if isinstance(child, SimpleWrap) and isinstance(child.dp, (Mux, IdentityDP)):
                    # Muxes and identities could be optimized away
                    # and disappear
                    continue
                elif isinstance(child, CompositeNamedDP) and not child.get_name2ndp():
                    # if the CompositeNamedDP is empty, then we don't have any output
                    # here. however we know that the child_imp is only:
                    child_imp = {}
                    # and we can create it on the fly:
                    children_artifact[child_name] = ndp_make(child, child_imp, context)
                    continue
                else: 
                    msg = 'Could not find artifact for child.'
                    raise_desc(DPInternalError, msg,
                                child_name=child_name,
                                imp_dict=imp_dict,
                                child=child.repr_long())
            else:
                child_imp = imp_dict[child_name]
                children_artifact[child_name] = ndp_make(child, child_imp, context)

        return run_make(ndp, children_artifact, context)

    elif isinstance(ndp, SimpleWrap):
        return run_make(ndp, imp_dict, context)

    elif isinstance(ndp, NamedDPCoproduct):
        for label in ndp.labels:
            if label in imp_dict:
                index = ndp.labels.index(label)
                child = ndp.ndps[index]
                value = imp_dict[label]
                return run_make(child, value, context)
        assert False 
    elif isinstance(ndp, LabelerNDP):
        msg = 'Bug: you should not run make() on the labeled version.'
        raise_desc(DPInternalError, msg)
    else:
        raise NotImplementedError(type(ndp))
    
def run_make(ndp, subresult, context):
    makes = get_make_functions(ndp)
    assert isinstance(makes, list)
    res = {}

    # removing the
    if isinstance(subresult, dict):
        # subresult = dict((k, v) for (k, v) in subresult.items() if k[0] != '_')
        subresult = dict((k, v) for (k, v) in subresult.items())

    for k, function in makes:
        a = MakeArguments(ndp=ndp,
                          subresult=subresult,
                          result=res,
                          key=k,
                          context=context)
        result = function(a)
        if result is None:
            msg = 'Did not expect None as a result from %r.' % function
            raise_desc(ValueError, msg, result=result, function=function)
        if k == 'root':
            res.update(result)
        else:
            res[k] = result
    return res
    
    
