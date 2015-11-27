# -*- coding: utf-8 -*-

from .poset import NotLeq
from contracts import raise_wrapped
from mocdp.posets.find_poset_minima.baseline_n2 import poset_minima

__all__ = [
    'check_minimal',
    'poset_check_chain',
]

def check_minimal(elements, poset):
    m2 = poset_minima(elements, poset.leq)
    if not len(m2) == len(elements):
        msg = 'Set of elements is not minimal: %s' % elements
        raise ValueError(msg)


def poset_check_chain(poset, chain):
    """ Raises an exception if the chain is not a chain. """
    for i in range(len(chain) - 1):
        try:
            poset.check_leq(chain[i], chain[i + 1])
        except NotLeq as e:
            msg = ('Fails for i = %s: %s ≰ %s' % (i, chain[i], chain[i + 1]))
            raise_wrapped(ValueError, e, msg, compact=True, chain=chain, poset=poset)

    return True
