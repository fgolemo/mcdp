# -*- coding: utf-8 -*-

from .find_poset_minima.baseline_n2 import poset_minima
from contracts import raise_wrapped
from mcdp_posets import NotLeq
from mcdp_posets.find_poset_minima.baseline_n2 import poset_maxima

__all__ = [
    'check_minimal',
    'check_maximal',
    'poset_check_chain',
]

def check_maximal(elements, poset):
    m2 = poset_maxima(elements, poset.leq)
    if not len(m2) == len(elements):
        msg = 'Set of elements is not minimal: %s' % elements
        raise ValueError(msg)

def check_minimal(elements, poset):
    m2 = poset_minima(elements, poset.leq)
    if not len(m2) == len(elements):
        msg = 'Set of elements is not minimal: %s' % elements
        extra = set(elements) - set(m2)
        x = ", ".join([ '%s %r' % (poset.format(s), s) for s in extra])
        msg += '\nThese points were dominated: %s' %x 
        if len(extra) == 1:
            e = list(extra)[0]
            for e2 in elements:
                if e2 == e: continue
                if poset.leq(e2, e):
                    msg += '\nDominated by %s %r' % (poset.format(e2), e2)

        raise ValueError(msg)


def poset_check_chain(poset, chain):
    """ Raises an exception if the chain is not a chain. """
    chain = list(chain)
    for i in range(len(chain) - 1):
        try:
            poset.check_leq(chain[i], chain[i + 1])
        except NotLeq as e:
            msg = ('Fails for i = %s: %s ≰ %s' % (i, chain[i], chain[i + 1]))
            raise_wrapped(ValueError, e, msg, compact=True, chain=chain, poset=poset)

    return True
