# -*- coding: utf-8 -*-
from abc import ABCMeta

from contracts import raise_wrapped
from contracts.enabling import all_disabled


__all__ = [
    'SpaceMeta',
    'decorate_methods',
]

class SpaceMeta(ABCMeta):
    # we use __init__ rather than __new__ here because we want
    # to modify attributes of the class *after* they have been
    # created
    def __init__(cls, name, bases, dct):  # @NoSelf
        ABCMeta.__init__(cls, name, bases, dct)
        method2dec = {
            'belongs': decorate_belongs,
        }
        if all_disabled():
            # print('Removing extra checks on Spaces')
            pass
        else:
            decorate_methods(cls, name, bases, dct, method2dec)

def decorate_belongs(f):
    def bel(self, x):
        from .space import NotBelongs
        try:
            f(self, x)
        except NotBelongs as e:
            msg = 'Point does not belong to space.'
            raise_wrapped(NotBelongs, e, msg, space=self, x=x, compact=True)
        return f
    return bel

def decorate_methods(cls, name, bases, dct, method2dec):  # @UnusedVariable
    for method_name, decorator in method2dec.items():
        if method_name in cls.__dict__:
            orig = cls.__dict__[method_name]
            decorated = decorator(orig)
            setattr(cls, method_name, decorated)
            # Note: removed the else clause that was unreachable
            # In Python 3, for-else means the else runs if the loop completes without a break
            # The original code had an else directly under an if, making it unreachable
