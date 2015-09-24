# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from contracts import contract
from contracts.utils import raise_wrapped
import warnings

class NotBelongs(Exception):
    pass


class SpaceMeta(ABCMeta):
    # we use __init__ rather than __new__ here because we want
    # to modify attributes of the class *after* they have been
    # created
    def __init__(cls, name, bases, dct):  # @NoSelf
        ABCMeta.__init__(cls, name, bases, dct)
#         print cls.__dict__

        if 'belongs' in cls.__dict__:  # for example,
            belongs = cls.__dict__['belongs']

            def dec(f):
                def bel(self, x):
                    try:
                        f(self, x)
                    except NotBelongs as e:
                        msg = 'Point does not belong to space.'
                        raise_wrapped(NotBelongs, e, msg, space=self, x=x)
                return f
            setattr(cls, 'belongs', dec(belongs))
        else:
            warnings.warn("Not decorating %s :%s " % (name, cls))

class Space():
    __metaclass__ = SpaceMeta

    def format(self, x):
        """ Formats a point in the space. """
        return x.__repr__()

    @abstractmethod
    def belongs(self, x):
        pass


class Map():

    __metaclass__ = ABCMeta

    @abstractmethod
    @contract(returns=Space)
    def get_domain(self):
        pass

    @abstractmethod
    @contract(returns=Space)
    def get_codomain(self):
        pass

    @abstractmethod
    def __call__(self, x):
        pass

    def __repr__(self):
        return "%s->%s" % (self.get_domain(), self.get_codomain())
