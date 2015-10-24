# -*- coding: utf-8 -*-
from .poset import NotLeq, Poset
from .space_product import SpaceProduct
from contracts import contract
from contracts.utils import indent, raise_desc

__all__ = [
    'PosetProduct',
]


class PosetProduct(SpaceProduct, Poset):
    """ A product of Posets with the product order. """
    @contract(subs='seq(str|$Poset|code_spec)')
    def __init__(self, subs):
        from mocdp.configuration import get_conftools_posets
        library = get_conftools_posets()
        subs = tuple([library.instance_smarter(s)[1] for s in subs])
        SpaceProduct.__init__(self, subs)

    def check_leq(self, a, b):
        self.belongs(a)
        self.belongs(b)
        problems = []
        for i, (sub, x, y) in enumerate(zip(self.subs, a, b)):
            try:
                sub.check_leq(x, y)
            except NotLeq as e:
                msg = '#%d (%s): %s ≰ %s.' % (i, sub, x, y)
                msg += '\n' + indent(str(e).strip(), '| ')
                problems.append(msg)
        if problems:
            msg = 'Leq does not hold.\n'
            msg = "\n".join(problems)
            raise_desc(NotLeq, msg, self=self, a=a, b=b)

    def get_top(self):
        return tuple([s.get_top() for s in self.subs])

    def get_bottom(self):
        return tuple([s.get_bottom() for s in self.subs])

    def get_test_chain(self, n):
        """
            Returns a test chain of length n
        """
        chains = [s.get_test_chain(n) for s in self.subs]
        res = zip(*tuple(chains))
        return res


