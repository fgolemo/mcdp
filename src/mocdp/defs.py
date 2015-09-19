from contracts import contract
from abc import ABCMeta, abstractmethod


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

    @abstractmethod
    def leq(self, a, b):
        pass


class Interval(Poset):
    def __init__(self, L, U):
        assert L <= U
        self.L = L
        self.U = U
        
    def get_bottom(self):
        return self.L

    def get_top(self):
        return self.U

    def leq(self, a, b):
        return a <= b

    def belongs(self, x):
        if not isinstance(x, float):
            raise ValueError('Not float')
        if not self.L <= x <= self.U:
            msg = 'Not valid %s <= %s <= %s' % (self.L, x, self.U)
            raise ValueError(msg)
        return True

class Rcomp(Poset):
    def __init__(self):
        self.top = "T"
        pass

    def get_bottom(self):
        return 0.0

    def get_top(self):
        return self.top
    
    def belongs(self, x):
        if x == self.top: return True
        if not isinstance(x, float):
            raise ValueError('Not float')
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
    def __init__(self, minimals, poset):
        self.minimals = minimals
        self.poset = poset

class PrimitiveDP():
    __metaclass__ = ABCMeta

    @abstractmethod
    @contract(returns=Space)
    def get_func_space(self):
        pass

    @abstractmethod
    @contract(returns=Poset)
    def get_res_space(self):
        pass

    @abstractmethod
    @contract(returns=UpperSet)
    def solve(self, func):
        '''
            Given one func point,
            Returns an UpperSet 
        '''
        pass
