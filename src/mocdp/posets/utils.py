# -*- coding: utf-8 -*-

from .poset import NotLeq
from contracts import raise_wrapped

__all__ = [
    'check_minimal',
    'poset_minima',
    'poset_check_chain',
]

def check_minimal(elements, poset):
    m2 = poset_minima(elements, poset.leq)
    if not len(m2) == len(elements):
        msg = 'Set of elements is not minimal: %s' % elements
        raise ValueError(msg)

def poset_minima(elements, leq):
    """ Find the minima of a poset according to given comparison 
        function. For small sets only - O(n^2). """
    res = []
    for e in elements:
        # nobody is less than it
        # should_add = all([not leq(r, e) for r in res])
        for r in res:
            if leq(r, e):
                should_add = False
                break
        else:
            should_add = True
        
        if should_add:
            # remove the ones that are less than this
            res = [r for r in res if not leq(e, r)] + [e]
    return res

def poset_check_chain(poset, chain):
    """ Raises an exception if the chain is not a chain. """
    for i in range(len(chain) - 1):
        try:
            poset.check_leq(chain[i], chain[i + 1])
        except NotLeq as e:
            msg = ('Fails for i = %s: %s ≰ %s' % (i, chain[i], chain[i + 1]))
            raise_wrapped(ValueError, e, msg, compact=True, chain=chain, poset=poset)

    return True
