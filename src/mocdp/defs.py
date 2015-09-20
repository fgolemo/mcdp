# -*- coding: utf-8 -*-

from contracts import contract
from abc import ABCMeta, abstractmethod
from contracts.utils import check_isinstance


class Space():
    __metaclass__ = ABCMeta
#
#     @abstractmethod
#     def get_name(self):
#         pass
#
#     @abstractmethod
#     def get_units(self):
#         pass
#
#     @abstractmethod
#     def get_comment(self):
#         pass
    
    @abstractmethod
    def belongs(self, x):
        pass
    
class NotLeq(Exception):
    pass
class NotBelongs(Exception):
    pass

class Poset(Space):

    @abstractmethod
    def get_bottom(self):
        pass

    def get_top(self):
        pass

    def get_bot(self):
        return self.get_bottom()

    def get_test_chain(self, n):
        """
            Returns a test chain of length n
        """
        return [self.get_bottom(), self.get_top()]

    def leq(self, a, b):
        try:
            self.check_leq(a, b)
            return True
        except NotLeq:
            return False

    @abstractmethod
    def check_leq(self, a, b):
        # raise NotLeq if not a <= b
        pass

class Interval(Poset):
    def __init__(self, L, U):
        assert L <= U
        self.L = float(L)
        self.U = float(U)
        self.belongs(self.L)
        self.belongs(self.U)
        assert self.leq(self.L, self.U)

    def get_test_chain(self, n):
        import numpy as np
        res = np.linspace(self.L, self.U, n)
        return list(res)

    def get_bottom(self):
        return self.L

    def get_top(self):
        return self.U

    def check_leq(self, a, b):
        if not(a <= b):
            raise NotLeq('%s ≰ %s')

    def belongs(self, x):
        check_isinstance(x, float)
        if not self.L <= x <= self.U:
            msg = '!(%s ≤ %s ≤ %s)' % (self.L, x, self.U)
            raise NotBelongs(msg)
        return True

    def __repr__(self):
        return "[%s,%s]" % (self.L, self.U)

class RcompTop():
    def __repr__(self):
        return "⊤"
    def __eq__(self, x):
        return isinstance(x, RcompTop)
    def __hash__(self):
        return 42  # "RCompTop"

class Rcomp(Poset):
    def __init__(self):
        self.top = RcompTop()


    def get_bottom(self):
        return 0.0

    def get_top(self):
        return self.top
    
    def belongs(self, x):
        if x == self.top:
            return True

        check_isinstance(x, float)
        if not 0 <= x:
            msg = '%s ≰ %s' % (0, x)
            raise ValueError(msg)
        return True
    
    def __repr__(self):
        return "ℜ⋃{⊤}"
        
    def _leq(self, a, b):
        if a == b:
            return True
        if a == self.top:
            return False
        if b == self.top:
            return True
        return a <= b

    def check_leq(self, a, b):
        if not self._leq(a, b):
            raise NotLeq()

class ProductSpace(Poset):

    @contract(subs='dict(str:$Poset)')
    def __init__(self, subs):
        self.subs = subs


class UpperSet():
    def __init__(self, minimals, P):
        self.minimals = minimals
        self.P = P

        for m in minimals:
            self.P.belongs(m)

        from mocdp.poset_utils import check_minimal
        check_minimal(minimals, P)


    def __repr__(self):  # ≤  ≥
        return "∪".join("{x∣ x ≥ %s}" % m for m in self.minimals)


class EmptySet():
    def __init__(self, P):
        self.P = P

    def __repr__(self):
        return "∅"
    
    def __eq__(self, other):
        return isinstance(other, EmptySet) and other.P == self.P


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
        check_isinstance(x, UpperSet)
        if not isinstance(x, UpperSet):
            msg = 'Not an upperset: %s' % x
            raise NotBelongs(msg)
        if not x.P == self.P:
            msg = 'Different poset: %s ≠ %s' % (self.P, x.P)
            raise NotBelongs(msg)
        return True 
        
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
        self.my_leq_(b, a)

    def my_leq_(self, A, B):
        # there exists an a in A that a <= b
        def dominated(b):
            for a in A.minimals:
                if self.P.leq(a, b):
                    return True
            return False


        # for all elements in B
        for b in B.minimals:
            if not dominated(b):
                raise NotLeq("b = %s not dominated by any a in %s" % (b, A.minimals))


    def __repr__(self):
        return "UpperSets(%r)" % self.P

class PrimitiveDP():
    __metaclass__ = ABCMeta

    @abstractmethod
    @contract(returns=Space)
    def get_fun_space(self):
        pass

    @abstractmethod
    @contract(returns=Poset)
    def get_res_space(self):
        pass

    @contract(returns=Poset)
    def get_tradeoff_space(self):
        return UpperSets(self.get_res_space())

    @abstractmethod
    @contract(returns=UpperSet)
    def solve(self, func):
        '''
            Given one func point,
            Returns an UpperSet 
        '''
        pass
