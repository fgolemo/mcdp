# -*- coding: utf-8 -*-
from .poset import NotLeq, Poset
from .space import NotBelongs
from contracts import contract

__all__ = [
    'PosetProduct',
]


class PosetProduct(Poset):
    """ A product of Posets with the product order. """
    @contract(subs='seq(str|$Poset|code_spec)')
    def __init__(self, subs):
        from mocdp.configuration import get_conftools_posets
        library = get_conftools_posets()
        self.subs = tuple([library.instance_smarter(s)[1] for s in subs])

    def get_top(self):
        return tuple([s.get_top() for s in self.subs])

    def get_bottom(self):
        return tuple([s.get_bottom() for s in self.subs])

    def check_leq(self, a, b):
        problems = []
        for i, (sub, x, y) in enumerate(zip(self.subs, a, b)):
            try:
                sub.check_leq(x, y)
            except NotLeq as e:
                msg = '#%d (%s): %s ≰ %s: %s' % (i, sub, x, y, e)
                problems.append(msg)
        if problems:
            msg = "\n".join(problems)
            raise NotLeq(msg)

    def belongs(self, x):
        problems = []
        for i, (sub, xe) in enumerate(zip(self.subs, x)):
            try:
                sub.belongs(xe)
            except NotBelongs as e:
                msg = '#%d (%s): %s does not belong: %s' % (i, sub, xe, e)
                problems.append(msg)

        if problems:
            msg = "\n".join(problems)
            raise NotBelongs(msg)

    def format(self, x):
        ss = []
        for _, (sub, xe) in enumerate(zip(self.subs, x)):
            ss.append(sub.format(xe))

        return '(' + ', '.join(ss) + ')'

    def get_test_chain(self, n):
        """
            Returns a test chain of length n
        """
        chains = [s.get_test_chain(n) for s in self.subs]
        res = zip(*tuple(chains))
        return res

    def __repr__(self):
        return "×".join([str(s) for s in self.subs])

    def __eq__(self, other):
        return isinstance(other, PosetProduct) and other.subs == self.subs
