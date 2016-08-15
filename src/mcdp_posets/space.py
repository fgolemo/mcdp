# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from contracts import contract, raise_wrapped
from mocdp.exceptions import do_extra_checks
from .space_meta import SpaceMeta

class NotBelongs(Exception):
    pass

class Belongs(Exception):
    """ The point actually belongs to the set
        raised by check_not_belongs """
    pass

class NotEqual(Exception):
    pass

class Uninhabited(Exception):
    ''' There is no element in this space. Raised by witness().'''
    pass

class Space(object):
    __metaclass__ = SpaceMeta

    def format(self, x):
        """ Formats a point in the space. """
        return x.__repr__()

    @abstractmethod
    def belongs(self, x):
        """ Raise NotBelongs """
    
    def check_belongs(self, x):
        return self.belongs(x)
    
    def check_not_belongs(self, x):
        try:
            self.check_belongs(x)
        except NotBelongs:
            return
        else:
            raise Belongs()

    @abstractmethod
    def check_equal(self, x, y):
        # Raise NotEqual if not
        pass


    def equal(self, a, b):
        try:
            self.check_equal(a, b)
        except NotEqual:
            return False
        else:
            return True
        
    @abstractmethod
    def witness(self):
        """ Returns an element of the space, or raise Uninhabited
            if the space is empty. """
        pass

    def repr_long(self):
        return self.__repr__()


class MapNotDefinedHere(Exception):
    """ The map is not defined at this point """

class Map():

    __metaclass__ = ABCMeta

    def __init__(self, dom, cod):
        self.dom = dom
        self.cod = cod

    @contract(returns=Space)
    def get_domain(self):
        return self.dom

    @contract(returns=Space)
    def get_codomain(self):
        return self.cod

    def __call__(self, x):
        if do_extra_checks():
            D = self.get_domain()
            try:
                D.belongs(x)
            except NotBelongs as e:
                msg = 'Point does not belong to domain.'
                raise_wrapped(NotBelongs, e, msg, map=self, x=x, domain=D)

        y = self._call(x)

        if do_extra_checks():

            C = self.get_codomain()
            try:
                C.belongs(y)
            except NotBelongs as e:
                msg = 'Point does not belong to codomain.'
                raise_wrapped(NotBelongs, e, msg, map=self, y=y, codomain=C)

        return y

    @abstractmethod
    def _call(self, x):
        """ Might raise MapNotDefinedHere (hack) """
        pass

    def __repr__(self):
        return "%s:%s→%s" % (type(self).__name__,
                             self.get_domain(), self.get_codomain())
