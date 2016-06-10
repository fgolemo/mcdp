# -*- coding: utf-8 -*-
import functools
import inspect
import sys

def parse_action(f):
    """
    Decorator for pyparsing parse actions to ease debugging.

    pyparsing uses trial & error to deduce the number of arguments a parse
    action accepts. Unfortunately any ``TypeError`` raised by a parse action
    confuses that mechanism.

    This decorator replaces the trial & error mechanism with one based on
    reflection. If the decorated function itself raises a ``TypeError`` then
    that exception is re-raised if the wrapper is called with less arguments
    than required. This makes sure that the actual ``TypeError`` bubbles up
    from the call to the parse action (instead of the one caused by pyparsing's
    trial & error).
    """
    num_args = len(inspect.getargspec(f).args)
    if num_args > 3:
        raise ValueError('Input function must take at most 3 parameters.')

    @functools.wraps(f)
    def action(*args):
        if len(args) < num_args:
            if action.exc_info:
                raise action.exc_info[0], action.exc_info[1], action.exc_info[2]
        action.exc_info = None
        try:
            return f(*args[:-(num_args + 1):-1])
        except TypeError as e:  # @UnusedVariable
            action.exc_info = sys.exc_info()
            raise

    action.exc_info = None
    return action

def isnamedtupleinstance(x):
    t = type(x)
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple: return False
    f = getattr(t, '_fields', None)
    if not isinstance(f, tuple): return False
    return all(type(n) == str for n in f)

