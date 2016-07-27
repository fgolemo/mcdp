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
from mocdp import ATTRIBUTE_NDP_RECURSIVE_NAME, ATTRIBUTE_NDP_MAKE_FUNCTION
from mocdp.comp.composite import CompositeNamedDP, cndp_get_name_ndp_notfunres, \
    cndp_iterate_res_nodes, cndp_iterate_fun_nodes
from mocdp.comp.wrap import SimpleWrap
from contracts.utils import raise_desc
from mcdp_posets.space_product import SpaceProduct
from mcdp_posets.category_coproduct import Coproduct1Labels
from contracts import contract
from mocdp.ndp.named_coproduct import NamedDPCoproduct
from mcdp_dp.dp_flatten import Mux
from mcdp_dp.dp_identity import IdentityDP
from collections import namedtuple

__all__ = [
    'label_with_recursive_names',
]

def label_with_recursive_names(ndp):
    visit_hierarchy(ndp, label_with_recursive_name_)

def label_with_recursive_name_(parents_names, yourname, ndp):
    recursive_name = filter(None, parents_names + (yourname,))
    print('labeling %s' % recursive_name.__repr__())
    if recursive_name != ():
        setattr(ndp, ATTRIBUTE_NDP_RECURSIVE_NAME, recursive_name)

def visit_hierarchy(ndp0, func):
    """
        Visits the hierarchy in deep first
    """

    def visit(parents_name, yourname, ndp):

        if isinstance(ndp, CompositeNamedDP):
                for name, child in cndp_get_name_ndp_notfunres(ndp):
                    visit(parents_name + (yourname,), name, child)

                for fname, child in cndp_iterate_fun_nodes(ndp):
                    visit(parents_name + (yourname,), fname, child)

                for rname, child in cndp_iterate_res_nodes(ndp):
                    visit(parents_name + (yourname,), rname, child)

        elif isinstance(ndp, SimpleWrap):
            func(parents_name, yourname, ndp)
            pass
        elif isinstance(ndp, NamedDPCoproduct):
            # func(parents_name, yourname, ndp)
            assert len(ndp.ndps) == len(ndp.labels), ndp
            for child, label in zip(ndp.ndps, ndp.labels):
                visit(parents_name + (yourname,), label, child)
        else:
            assert False

    visit(parents_name=(), yourname=None, ndp=ndp0)

def get_names_used(I):
    """
        I = SpaceProduct, with some marked as ATTRIBUTE_NDP_RECURSIVE_NAME.
    
        Returns list of names or None.
    """
    if hasattr(I, ATTRIBUTE_NDP_RECURSIVE_NAME):
        return [getattr(I, ATTRIBUTE_NDP_RECURSIVE_NAME)]
    
    if isinstance(I, SpaceProduct):
        res = []
        for j, sub in enumerate(I.subs):
            if hasattr(sub, ATTRIBUTE_NDP_RECURSIVE_NAME):
                name = getattr(sub, ATTRIBUTE_NDP_RECURSIVE_NAME)
                assert isinstance(name, tuple)
                res.append(name)
            else:
                res.append(None)
        assert len(res) == len(I.subs)
        return res

    return []
        
@contract(returns=dict)
def collect(I, imp):
    if hasattr(I, ATTRIBUTE_NDP_RECURSIVE_NAME):
        name = getattr(I, ATTRIBUTE_NDP_RECURSIVE_NAME)
        return {name: imp}

    I.belongs(imp)
    res = {}
    if isinstance(I, SpaceProduct):
        for j, sub in enumerate(I.subs):
            res.update(**collect(sub, imp[j]))

    elif isinstance(I, Coproduct1Labels):
        i, xi = I.unpack(imp)
        res.update(**collect(I.spaces[i], xi))
    else:
        pass
        # raise(NotImplementedError(type(I)))

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
    if hasattr(ndp, ATTRIBUTE_NDP_MAKE_FUNCTION):
        return getattr(ndp, ATTRIBUTE_NDP_MAKE_FUNCTION)
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
                    msg = 'Could not find artifact for child'
                    raise_desc(Exception, msg, child_name=child_name, imp_dict=imp_dict,
                               child=child.repr_long())
            else:
                child_imp = imp_dict[child_name]
                children_artifact[child_name] = ndp_make(child, child_imp, context)

        return run_make(ndp, children_artifact, context)

    elif isinstance(ndp, SimpleWrap):
        return run_make(ndp, imp_dict, context)

    elif isinstance(ndp, NamedDPCoproduct):
        # print('imp_dict: %s' % imp_dict.__repr__())
        # if True:
        for label in ndp.labels:
            if label in imp_dict:
                index = ndp.labels.index(label)
                child = ndp.ndps[index]
                value = imp_dict[label]
                return run_make(child, value, context)
        assert False 
    else:
        raise NotImplementedError(type(ndp))
    
def run_make(ndp, subresult, context):
    makes = get_make_functions(ndp)
    assert isinstance(makes, list)
    res = {}

    # removing the
    if isinstance(subresult, dict):
        subresult = dict((k, v) for (k, v) in subresult.items() if k[0] != '_')

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
    
    
