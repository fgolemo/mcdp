# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from contracts import contract
from mcdp_posets import PosetProduct


__all__ = [
    'NotConnected',
    'NamedDP',
]

class NotConnected(Exception):
    pass

class NamedDP():
    """ A DP with names """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_dp(self):
        pass

    @abstractmethod
    def check_fully_connected(self):
        """ Raise NotConnected """

    def is_fully_connected(self):
        try:
            self.check_fully_connected()
        except NotConnected:
            return False
        else:
            return True

    def flatten(self):
        return self

    def compact(self):
        return self

    @abstractmethod
    @contract(returns='isinstance(SimpleWrap)')
    def abstract(self):
        """ Returns a SimpleWrap """

    @abstractmethod
    @contract(returns='list(str)')
    def get_fnames(self):
        pass

    @abstractmethod
    @contract(returns='list(str)')
    def get_rnames(self):
        pass

    def rindex(self, rn):
        rnames = self.get_rnames()
        if len(rnames) == 1:
            return ()
        return rnames.index(rn)

    def findex(self, fn):
        fnames = self.get_fnames()
        if len(fnames) == 1:
            return ()
        return fnames.index(fn)

    @abstractmethod
    @contract(rname=str)
    def get_rtype(self, rname):
        pass

    @abstractmethod
    @contract(fname=str)
    def get_ftype(self, fname):
        pass

    def repr_long(self):
        return self.__repr__()

    @contract(signals='list|tuple')
    def get_ftypes(self, signals):
        # Returns the product space
        types = [self.get_ftype(s) for s in signals]
        return PosetProduct(tuple(types))

    @contract(signals='list|tuple')
    def get_rtypes(self, signals):
        # Returns the product space
        types = [self.get_rtype(s) for s in signals]
        return PosetProduct(tuple(types))




