# -*- coding: utf-8 -*-
from .poset import NotLeq, Poset
from .space import NotBelongs, NotEqual
from .utils import poset_minima
from contracts import check_isinstance, contract
from contracts.utils import raise_desc

__all__ = [
    'UpperSet',
    'UpperSets',
]

class UpperSet():
    @contract(minimals='set|list', P=Poset)
    def __init__(self, minimals, P):
        self.minimals = frozenset(minimals)
        self.P = P

#         if len(self.minimals) == 0:
#             msg = 'Cannot create upper set from empty set.'
#             raise_desc(ValueError, msg, P=self.P)


        problems = []
        for m in minimals:
            try:
                self.P.belongs(m)
            except NotBelongs as e:
                problems.append(e)
        if problems:
            msg = "Cannot create upper set:\n"
            msg += "\n".join(str(p) for p in problems)
            raise NotBelongs(msg)

        from .utils import check_minimal
        check_minimal(minimals, P)

    @contract(returns=Poset)
    def get_poset(self):
        return self.P

    def __repr__(self):  # ≤  ≥
        contents = " v ".join("x ≥ %s" % self.P.format(m)
                        for m in sorted(self.minimals))

        return "{x ∣ %s }" % contents
#         return "∪".join("{x∣ x ≥ %s}" % self.P.format(m)
#                         for m in self.minimals)


class UpperSets(Poset):

    @contract(P='$Poset|str')
    def __init__(self, P):
        from mocdp.configuration import get_conftools_posets
        _, self.P = get_conftools_posets().instance_smarter(P)

        self.top = self.get_top()
        self.bot = self.get_bottom()

        self.belongs(self.top)
        self.belongs(self.bot)
        assert self.leq(self.bot, self.top)
        assert not self.leq(self.top, self.bot)  # unless empty

    def get_bottom(self):
        x = self.P.get_bottom()
        return UpperSet(set([x]), self.P)

    def get_top(self):
        x = self.P.get_top()
        return UpperSet(set([x]), self.P)

    def get_test_chain(self, n):
        chain = self.P.get_test_chain(n)
        f = lambda x: UpperSet(set([x]), self.P)
        return map(f, chain)

    def belongs(self, x):
#         check_isinstance(x, UpperSet)
        if not isinstance(x, UpperSet):
            msg = 'Not an upperset: %s' % x.__repr__()
            raise NotBelongs(msg)
        if not x.P == self.P:
            msg = 'Different poset: %s ≠ %s' % (self.P, x.P)
            raise NotBelongs(msg)
        return True

    def check_equal(self, a, b):
        m1 = a.minimals
        m2 = b.minimals
        if not (m1 == m2):
            raise NotEqual('%s ≠ %s' % (m1, m2))

    def check_leq(self, a, b):
        self.belongs(a)
        self.belongs(b)
        if a == b:
            return True
        if a == self.bot:
            return True
        if b == self.top:
            return True
        if b == self.bot:
            raise NotLeq('b = my ⊥')

        if a == self.top:
            raise NotLeq('a = my ⊤')

        self.my_leq_(a, b)
        # XXX: not sure I should add this, with inverted
#         self.my_leq_(b, a, inverted)

    def my_leq_(self, A, B):
        # there exists an a in A that a <= b
        def dominated(b):
            problems = []
            for a in A.minimals:
                try:
                    # if inverted: self.P.check_leq(b, a)
                    self.P.check_leq(a, b)
                    return True, None
                except NotLeq as e:
                    problems.append(e)
            return False, problems


        # for all elements in B
        for b in B.minimals:
            is_dominated, whynot = dominated(b)
            if not is_dominated:
                msg = "b = %s not dominated by any a in %s" % (b, A.minimals)
                msg += '\n' + '\n- '.join(map(str, whynot))
                raise NotLeq(msg)

    def meet(self, a, b):  # "min" ∨
        # To compute the meet (min) of two upper sets
        # just take the union of the minimal elements
        # (without redundant elements)
        elements = set()
        elements.update(a.minimals)
        elements.update(b.minimals)
        elements0 = poset_minima(elements, self.P.leq)
        r = UpperSet(elements0, self.P)
        self.check_leq(r, a)
        self.check_leq(r, b)
        return r

    def format(self, x):
        contents = " v ".join("x ≥ %s" % self.P.format(m)
                        for m in sorted(x.minimals))

        return "{x ∣ %s }" % contents


    def __repr__(self):
        return "Upsets(%r)" % self.P
