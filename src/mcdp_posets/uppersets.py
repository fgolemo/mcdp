# -*- coding: utf-8 -*-
from .find_poset_minima.baseline_n2 import poset_minima
from .poset import NotBounded, NotLeq, Poset
from .poset_product import PosetProduct
from .space import NotBelongs, NotEqual, Space, Uninhabited
from contracts import contract
from contracts.utils import raise_desc
from mocdp.exceptions import do_extra_checks, mcdp_dev_warning
import random

__all__ = [
    'UpperSet',
    'UpperSets',
    'LowerSet',
    # 'LowerSets',
    'lowerset_product',
    'upperset_product',
]

class UpperSet(Space):
    
    @contract(minimals='set|list|$frozenset', P=Poset)
    def __init__(self, minimals, P):
        self.minimals = frozenset(minimals)
        self.P = P

        if do_extra_checks():
            # XXX
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

            from mcdp_posets import check_minimal
            check_minimal(self.minimals, P)

    def witness(self):
        if not self.minimals:
            raise Uninhabited()
        n = len(self.minimals)
        i = random.randint(0, n - 1)
        return list(self.minimals)[i]

    @contract(returns=Poset)
    def get_poset(self):
        return self.P
    
    def check_equal(self, x, y):
        self.P.check_equal(x, y)

    def belongs(self, x):
        self.P.belongs(x)
        for p in self.minimals:
            if self.P.leq(p, x):
                return
        raise_desc(NotBelongs, 'Point does not belong')

        
    def __repr__(self):
        contents = ", ".join(self.P.format(m)
                        for m in sorted(self.minimals))

        return "↑{%s}" % contents




class UpperSets(Poset):

    @contract(P='$Poset')
    def __init__(self, P):
        self.P = P
        if do_extra_checks:
            try:
                self.top = self.get_top()
                self.belongs(self.top)
                self.bot = self.get_bottom()
                self.belongs(self.bot)
                assert self.leq(self.bot, self.top)
                assert not self.leq(self.top, self.bot)  # unless empty
            except NotBounded:
                pass

    def witness(self):
        w = self.P.witness()
        return UpperSet([w], self.P)
        
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
        if not isinstance(x, UpperSet):
            msg = 'Not an upperset: %s' % x.__repr__()
            raise NotBelongs(msg)
        if not x.P == self.P:
            msg = 'Different poset: %s ≠ %s' % (self.P, x.P)
            raise_desc(NotBelongs, msg, self=self, x=x)
        return True

    def check_equal(self, a, b):
        m1 = a.minimals
        m2 = b.minimals
        if not (m1 == m2):
            msg = 'The two sets are not equal\n   %s\n!= %s' % (self.format(a), self.format(b))
            raise NotEqual(msg)

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

    def format0(self, x):
        contents = " v ".join("x ≥ %s" % self.P.format(m)
                        for m in sorted(x.minimals))

        return "{x ∣ %s }" % contents

    def format(self, x):
        contents = ", ".join(self.P.format(m)
                        for m in sorted(x.minimals))

        return "↑{%s}" % contents

    def __repr__(self):
        return "U(%r)" % self.P



@contract(s1=UpperSet, s2=UpperSet, returns=UpperSet)
def upperset_product(s1, s2):
    assert isinstance(s1, UpperSet), s1
    assert isinstance(s2, UpperSet), s2
    res = set(zip(s1.minimals, s2.minimals))
    P = PosetProduct((s1.P, s2.P))
    return UpperSet(res, P)

class LowerSet(Space):

    @contract(maximals='set|list|$frozenset', P=Poset)
    def __init__(self, maximals, P):
        self.maximals = frozenset(maximals)
        self.P = P

        if do_extra_checks():
            # XXX
            problems = []
            for m in maximals:
                try:
                    self.P.belongs(m)
                except NotBelongs as e:
                    problems.append(e)
            if problems:
                msg = "Cannot create upper set:\n"
                msg += "\n".join(str(p) for p in problems)
                raise NotBelongs(msg)

            mcdp_dev_warning('check_maximal()')
            # from mcdp_posets import check_maximal
            # check_maximal(self.minimals, P)

    def witness(self):
        if not self.maximals:
            raise Uninhabited()
        else:
            n = len(self.maximals)
            i = random.randint(0, n - 1)
            return list(self.maximals)[i]

    @contract(returns=Poset)
    def get_poset(self):
        return self.P

    def check_equal(self, x, y):
        self.P.check_equal(x, y)

    def belongs(self, x):
        self.P.belongs(x)
        for p in self.maximals:
            if self.P.leq(x, p):
                return
        raise_desc(NotBelongs, 'Point does not belong to lower set.')

    def __repr__(self):
        contents = ", ".join(self.P.format(m)
                        for m in sorted(self.maximals))

        return "↓{%s}" % contents

@contract(s1=LowerSet, s2=LowerSet, returns=LowerSet)
def lowerset_product(s1, s2):
    assert isinstance(s1, LowerSet), s1
    assert isinstance(s2, LowerSet), s2
    res = set(zip(s1.minimals, s2.minimals))
    P = PosetProduct((s1.P, s2.P))
    return LowerSet(res, P)


@contract(ss='tuple($LowerSet)', returns=LowerSet)
def lowerset_product_multi(ss):
    Ps = tuple(_.P for _ in ss)
    mins = tuple(_.maximals for _ in ss)
    res = set(zip(*mins))
    P = PosetProduct(Ps)
    return LowerSet(res, P)

@contract(ss='tuple($UpperSet)', returns=UpperSet)
def upperset_product_multi(ss):
    Ps = tuple(_.P for _ in ss)
    mins = tuple(_.minimals for _ in ss)
    res = set(zip(*mins))
    P = PosetProduct(Ps)
    return UpperSet(res, P)
