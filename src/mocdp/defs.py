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
    
class Poset(Space):

    @abstractmethod
    def get_bottom(self):
        pass

    def get_top(self):
        pass

    def get_bot(self): return self.get_bottom()

    @abstractmethod
    def leq(self, a, b):
        pass


class Interval(Poset):
    def __init__(self, L, U):
        assert L <= U
        self.L = float(L)
        self.U = float(U)
        self.belongs(self.L)
        self.belongs(self.U)
        assert self.leq(self.L, self.U)

    def get_bottom(self):
        return self.L

    def get_top(self):
        return self.U

    def leq(self, a, b):
        return a <= b

    def belongs(self, x):
        check_isinstance(x, float)
#         if not isinstance(x, float):
#             raise ValueError('Not float: %s' % x)
        if not self.L <= x <= self.U:
            msg = 'Not valid %s <= %s <= %s' % (self.L, x, self.U)
            raise ValueError(msg)
        return True

class RcompTop():
    def __repr__(self):
        return "T"
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
            msg = 'Not valid %s <= %s' % (0, x)
            raise ValueError(msg)
        return True
        
    def leq(self, a, b):
        if a == b: return True
        if a == self.top:
            return False
        if b == self.top:
            return True
        return a <= b

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

    def __repr__(self):
        return "|".join(">= %s" % m for m in self.minimals)

class EmptySet():
    def __init__(self, P):
        self.P = P

    def __repr__(self):
        return "{}"
    
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

    def belongs(self, x):
        check_isinstance(x, UpperSet)
        if not isinstance(x, UpperSet):
            msg = 'Not an upperset: %s' % x
            raise ValueError(msg)
        if not x.P == self.P:
            msg = 'Not same poset: %s != %s' % (self.P, x.P)
            raise ValueError(msg)
        return True 
        
    def leq(self, a, b):
        self.belongs(a)
        self.belongs(b)
        if a == b:
            return True
        if a == self.bot:
            return True
        if b == self.top:
            return True
        if b == self.bot:
            return False
        if a == self.top:
            return False

        return self.leq_(a, b) and self.leq_(b, a)

    def leq_(self, A, B):
        # there exists an a in A that a <= b
        def dominated(b):
            for a in A.minimals:
                if self.P.leq(a, b):
                    return True
            return False

        # for all elements in B
        for b in B.minimals:
            if not dominated(b):
                return False

        return True

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
