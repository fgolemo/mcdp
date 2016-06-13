# -*- coding: utf-8 -*-
from .space import Space
from abc import abstractmethod
from contracts import contract, describe_value
from mocdp.exceptions import do_extra_checks
from contracts.utils import raise_desc

__all__ = [
    'Poset',
    'NotLeq',
    'NotJoinable',
    'NotBounded',
    'Preorder',
]

class NotLeq(Exception):
    pass

class NotJoinable(Exception):
    pass

class NotMeetable(Exception):
    pass

class NotBounded(Exception):
    pass

class Preorder(Space):
    """
        A space with a transitive and reflexive relation.
        
        Not necessarily antisymmetric. So if a <= b and b <= a,
        not necessarily a == b.
    """
    @abstractmethod
    def check_leq(self, a, b):
        """ Return None if a<=b; otherwise raise NotLeq with a description """

    def leq(self, a, b):
        try:
            self.check_leq(a, b)
            return True
        except NotLeq:
            return False
        
class Poset(Preorder):

    @contract(returns='set')
    def get_minimal_elements(self):
        """ Returns a set of minimal elements. 
            If there is a bottom, this is set([bottom])
        """
        try:
            bottom = self.get_bottom()
            return set([bottom])
        except NotBounded:
            msg = 'Not bounded so not implemented.'
            raise_desc(NotImplementedError, msg, type=type(self))

    def get_bottom(self):
        msg = 'Bottom not available for %s.' % describe_value(self)
        raise NotBounded(msg)

    def get_bot(self):
        return self.get_bottom()

    def get_top(self):
        msg = 'Top not available for %s.' % describe_value(self)
        raise NotBounded(msg)

    def get_test_chain(self, n):  # @UnusedVariable
        """
            Returns a test chain of length up to n.
            
            Might raise Uninhabited.
        """
        chain = [self.get_bottom()]
        try:
            top = self.get_top()
            chain.append(top)
        except NotBounded:
            pass
        return chain


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
        if do_extra_checks():
            self.belongs(a)
        from mcdp_posets import UpperSet
        return UpperSet(set([a]), self)

    @contract(elements='seq|set')
    def Us(self, elements):
        elements = list(elements)
        if do_extra_checks():
            for e in elements:
                self.belongs(e)
                # XXX n^2
            from mcdp_posets import check_minimal
            check_minimal(elements, poset=self)
        from mcdp_posets import UpperSet
        return UpperSet(set(elements), self)
