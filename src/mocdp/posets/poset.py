# -*- coding: utf-8 -*-
from .space import Space
from abc import abstractmethod
from contracts import contract, describe_value

__all__ = [
    'Poset',
    'NotLeq',
    'NotJoinable',
    'NotBounded',
]

class NotLeq(Exception):
    pass

class NotJoinable(Exception):
    pass

class NotMeetable(Exception):
    pass

class NotBounded(Exception):
    pass

class Poset(Space):

    @abstractmethod
    def check_leq(self, a, b):
        # Return none if a<=b; otherwise raise NotLeq with a description
        pass

    def get_bottom(self):
        msg = 'Bottom not available for %s.' % describe_value(self)
        raise NotBounded(msg)

    def get_bot(self):
        return self.get_bottom()

    def get_top(self):
        msg = 'Top not available for %s.' % describe_value(self)
        raise NotBounded(msg)

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

    def join(self, a, b):  # "max" ∨
        if self.leq(a, b):
            return b
        if self.leq(b, a):
            return a

        msg = 'The join %s ∨ %s does not exist in %s.' % (a, b, self)
        raise NotJoinable(msg)

    def meet(self, a, b):  # "min" ∧
        if self.leq(a, b):
            return a
        if self.leq(b, a):
            return b

        msg = 'The meet %s ∧ %s does not exist in %s.' % (a, b, self)
        raise NotJoinable(msg)

    def U(self, a):
        """ Returns the principal upper set corresponding to the given a. """
        self.belongs(a)
        from .uppersets import UpperSet
        return UpperSet(set([a]), self)

    @contract(elements='seq|set')
    def Us(self, elements):
        elements = list(elements)
        for e in elements:
            self.belongs(e)
        # XXX n^2
        from .utils import check_minimal
        check_minimal(elements, poset=self)
        from .uppersets import UpperSet
        return UpperSet(set(elements), self)
