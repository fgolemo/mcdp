# -*- coding: utf-8 -*-
import itertools
import random

from contracts import contract
from contracts.utils import raise_desc, check_isinstance
from mocdp.exceptions import do_extra_checks, mcdp_dev_warning
from mocdp.memoize_simple_imp import memoize_simple

from .find_poset_minima.baseline_n2 import poset_maxima, poset_minima
from .poset import NotLeq, Poset
from .poset_product import PosetProduct
from .space import Map, NotBelongs, NotEqual, Space, Uninhabited


__all__ = [
    'UpperSet',
    'UpperSets',
    'LowerSet',
    'LowerSets',
    'lowerset_product',
    'upperset_product',
    'lowerset_project',
    'upperset_project',
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
        if do_extra_checks():
            top = self.get_top()
            bot = self.get_bottom()
            self.belongs(top)
            self.belongs(bot)
            assert self.leq(bot, top)
            assert not self.leq(top, bot)  # unless empty

    def witness(self):
        w = self.P.witness()
        return UpperSet([w], self.P)
        
    @memoize_simple
    def get_bottom(self):
        minimals = self.P.get_minimal_elements()
        return UpperSet(minimals, self.P)

    @memoize_simple
    def get_top(self):
        """ The top is the empty set. """
        return UpperSet([], self.P)

    def get_test_chain(self, n):
        if n >= 2:
                
            chain = self.P.get_test_chain(n-1)
            f = lambda x: UpperSet(set([x]), self.P)
            chain = list(map(f, chain))
            chain.append(self.get_top())
            return chain
        else:
            return [self.get_bottom()]

    def belongs(self, x):
        if not isinstance(x, UpperSet):
            msg = 'Not an upperset.'
            raise_desc(NotBelongs, msg, x=x)
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
        if a == b:
            return True
        bot = self.get_bottom()
        top = self.get_top()
        if a == bot:
            return True
        if b == top:
            return True
        if b == bot:
            raise NotLeq('b = my ⊥')

        if a == top:
            raise NotLeq('a = my ⊤')

        self.my_leq_(a, b)

    def leq(self, a, b):
        return self._my_leq_fast(a, b)

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

    def _my_leq_fast(self, A, B):
        # there exists an a in A that a <= b
        def dominated(b):
            for a in A.minimals:
                if self.P.leq(a, b):
                    return True
            return False

        # for all elements in B
        for b in B.minimals:
            is_dominated = dominated(b)
            if not is_dominated:
                return False

        return True

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
        return "UpperSets(%r)" % self.P
    
    def __str__(self):
        return "U(%s)" % self.P
 

class LowerSets(Poset):

    @contract(P='$Poset')
    def __init__(self, P):
        self.P = P
        self.top = self.get_top()
        self.bot = self.get_bottom()
        if do_extra_checks():
            self.belongs(self.top)
            self.belongs(self.bot)
            assert self.leq(self.bot, self.top)
            assert not self.leq(self.top, self.bot)  # unless empty

    def witness(self):
        w = self.P.witness()
        return LowerSet([w], self.P)

    mcdp_dev_warning('need to think about this')


    def get_bottom(self):
        maximals = self.P.get_maximal_elements()
        return LowerSet(set(maximals), self.P)

    def get_top(self):
        return LowerSet(set(), self.P)

    def get_test_chain(self, n):
        chain = reversed(self.P.get_test_chain(n))
        f = lambda x: LowerSet(set([x]), self.P)
        return map(f, chain)

    def belongs(self, x):
        if not isinstance(x, LowerSet):
            msg = 'Not a lower set.'
            raise NotBelongs(msg)
        if not x.P == self.P:
            mcdp_dev_warning('should we try casting?')
            msg = 'Different poset: %s ≠ %s' % (self.P, x.P)
            raise_desc(NotBelongs, msg, self=self, x=x)
        return True

    def check_equal(self, a, b):
        m1 = a.maximals
        m2 = b.maximals
        if not (m1 == m2):
            msg = 'The two sets are not equal\n   %s\n!= %s' % (self.format(a), self.format(b))
            raise NotEqual(msg)

    def check_leq(self, a, b):
        if do_extra_checks():
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
        # there exists an a in A that a >= b
        def dominated(b):
            problems = []
            for a in A.maximals:
                try:
                    # if inverted: self.P.check_leq(b, a)
                    self.P.check_leq(b, a)
                    return True, None
                except NotLeq as e:
                    problems.append(e)
            return False, problems

        # for all elements in B
        for b in B.maximals:
            is_dominated, whynot = dominated(b)
            if not is_dominated:
                msg = "b = %s not dominated by any a in %s" % (b, A.maximals)
                msg += '\n' + '\n- '.join(map(str, whynot))
                raise NotLeq(msg)

    def meet(self, a, b):  # "min" ∨
        # To compute the meet (min) of two upper sets
        # just take the union of the minimal elements
        # (without redundant elements)
        elements = set()
        elements.update(a.maximals)
        elements.update(b.maximals)
        elements0 = poset_maxima(elements, self.P.leq)
        r = LowerSet(elements0, self.P)
        self.check_leq(r, a)
        self.check_leq(r, b)
        return r

    def format(self, x):
        contents = ", ".join(self.P.format(m)
                        for m in sorted(x.maximals))

        return "↓{%s}" % contents

    def __repr__(self):
        return "L(%r)" % self.P



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

    def witness(self):
        if not self.maximals:
            raise Uninhabited()
        else:
            n = len(self.maximals)
            i = random.randint(0, n - 1)
            return list(self.maximals)[i]

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


@contract(s1=UpperSet, s2=UpperSet, returns=UpperSet)
def upperset_product(s1, s2):
    assert isinstance(s1, UpperSet), s1
    assert isinstance(s2, UpperSet), s2
    res = set(zip(s1.minimals, s2.minimals))
    P = PosetProduct((s1.P, s2.P))
    return UpperSet(res, P)

@contract(s1=LowerSet, s2=LowerSet, returns=LowerSet)
def lowerset_product(s1, s2):
    """ Not actually a product """
    assert isinstance(s1, LowerSet), s1
    assert isinstance(s2, LowerSet), s2
    res = set(zip(s1.maximals, s2.maximals))
    P = PosetProduct((s1.P, s2.P))
    return LowerSet(res, P)

@contract(s1=LowerSet, s2=LowerSet, returns=LowerSet)
def lowerset_product_good(s1, s2):
    """ The real product. """
    assert isinstance(s1, LowerSet), s1
    assert isinstance(s2, LowerSet), s2
    res = set(itertools.product(s1.maximals, s2.maximals))
    P = PosetProduct((s1.P, s2.P))
    return LowerSet(res, P)

@contract(ss='seq($LowerSet)', returns=LowerSet)
def lowerset_product_multi(ss):
    """ Not actually a product """
    Ps = tuple(_.P for _ in ss)
    mins = tuple(_.maximals for _ in ss)
    res = set(zip(*mins))
    P = PosetProduct(Ps)
    return LowerSet(res, P)

@contract(ss='seq($UpperSet)', returns=UpperSet)
def upperset_product_multi(ss):
    Ps = tuple(_.P for _ in ss)
    mins = tuple(_.minimals for _ in ss)
    res = set(itertools.product(*mins))
    P = PosetProduct(Ps)

    from operator import mul
    nout = len(res)
    lengths = [len(_.minimals) for _ in ss]
    ns = reduce(mul, lengths)
    assert nout == ns, (nout, lengths, ns)

    return UpperSet(res, P)

@contract(ur='$UpperSet', i='int,>=0')
def upperset_project(ur, i):
    """ Projects an upperset on a posetproduct to the i-th component. """
    check_isinstance(ur, UpperSet)
    check_isinstance(ur.P, PosetProduct)
    if not (0 <= i < len(ur.P)):
        msg = 'Index %d not valid.' % i
        raise_desc(ValueError, msg, P=ur.P)
    minimals = set()
    Pi = ur.P.subs[i]
    for m in ur.minimals:
        mi = m[i]
        minimals.add(mi)
    return UpperSet(poset_minima(minimals, leq=Pi.leq), P=Pi)

@contract(lf='$LowerSet', i='int,>=0')
def lowerset_project(lf, i):
    assert isinstance(lf, LowerSet), lf
    assert isinstance(lf.P, PosetProduct), lf
    if not (0 <= i < len(lf.P)):
        msg = 'Index %d not valid.' % i
        raise_desc(ValueError, msg, P=lf.P)
    maximals = set()
    Pi = lf.P.subs[i]
    for m in lf.maximals:
        mi = m[i]
        maximals.add(mi)
    return LowerSet(poset_maxima(maximals, leq=Pi.leq), P=Pi)



@contract(ur='$UpperSet', f='isinstance(Map)', returns='$UpperSet')
def upperset_project_map(ur, f):
    """ Projects the upper set through the given map. """
    check_isinstance(ur, UpperSet)
    check_isinstance(f, Map)
    from .types_universe import get_types_universe
    tu = get_types_universe()
    if do_extra_checks():
        tu.check_equal(ur.P, f.get_domain())
    Q = f.get_codomain()
    assert isinstance(Q, Poset)
    minimals = set()
    for m in ur.minimals:
        mi = f(m)
        minimals.add(mi)
    minimals = poset_minima(minimals, leq=Q.leq)
    return UpperSet(minimals, P=Q)
    
