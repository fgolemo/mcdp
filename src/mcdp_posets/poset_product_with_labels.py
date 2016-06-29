# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets.poset_product import PosetProduct
from mcdp_posets.space import NotBelongs
from contracts.utils import raise_desc

__all__ = [
    'PosetProductWithLabels',
]

class PosetProductWithLabels(PosetProduct):

    @contract(subs='seq[N]($Poset)', labels='seq[N](str)')
    def __init__(self, subs, labels):
        assert len(subs) == len(labels)
        self.labels = labels
        PosetProduct.__init__(self, subs)


    def format(self, x):
        if not isinstance(x, tuple):
            raise_desc(NotBelongs, 'Not a tuple', x=x, self=self)

        ss = []
        for label, sub, xe in zip(self.labels, self.subs, x):
            s = '%s:%s' % (label, sub.format(xe))
            ss.append(s)

        # 'MATHEMATICAL LEFT ANGLE BRACKET' (U+27E8) ⟨
        # 'MATHEMATICAL RIGHT ANGLE BRACKET'   ⟩
        return '⟨' + ', '.join(ss) + '⟩'

    def __repr__(self):
        ps = ['%s:%s' % (label, sub) for (label, sub) in zip(self.labels, self.subs)]
        p = ", ".join(ps)
        return "product(%s)" % p

