# -*- coding: utf-8 -*-
from contextlib import contextmanager
from contracts import all_disabled
import getpass
import sys


class MCDPException(Exception):
    pass


class MCDPExceptionWithWhere(MCDPException):
    def __init__(self, error, where=None, stack=None):
        if not isinstance(error, str):
            raise ValueError('Expected string, got %r.' % type(error))

        self.error = error
        self.where = where
        self.stack = stack
        
        MCDPException.__init__(self, error, where, stack)

    def __str__(self):
        error, where, stack = self.args
        assert isinstance(error, str), error
        s = ""
        if stack:
            s += '\n' + stack + '\n'
        s += error
        if where is not None:
            from contracts.interface import add_prefix
            ws = where.__str__()
            assert isinstance(ws, str), (ws, type(where))
            s += "\n\n" + add_prefix(ws, ' ')
        return s

    def with_filename(self, filename):
        """ Returns the same exception with reference
            to the given filename. """
        where = _get_where_with_filename(self, filename)
        return type(self)(self.error, where=where, stack=self.stack)


class DPInternalError(MCDPExceptionWithWhere):
    """ Internal consistency errors (not user) """


class DPUserError(MCDPExceptionWithWhere):
    """ User mistake """
    pass


class DPSyntaxError(DPUserError):
    pass


class DPSemanticError(DPUserError):
    pass

class DPNotImplementedError(DPInternalError):
    pass


class DPSemanticErrorNotConnected(DPSemanticError):
    pass


class DPUserAssertion(MCDPExceptionWithWhere):
    """ 
        Assertion thrown by user using assert_leq, etc. 
    """
    pass


@contextmanager
def extend_with_filename(realpath):
    try:
        yield
    except MCDPExceptionWithWhere as e:
        _type, _value, traceback = sys.exc_info()
        if e.where is None or e.where.filename is None:
            if realpath is not None:
                e = e.with_filename(realpath)
            else:
                e = e
        raise e, None, traceback

def _get_where_with_filename(e, filename):
    where = e.where
    
    if where is None:
        mcdp_dev_warning('warning, where is None here: %s' % e)
        where = None
    else:    
        where = where.with_filename(filename)
        
    return where

user = getpass.getuser()
# class _storage:
#     first = True

def do_extra_checks():
    res = not all_disabled()
#     if _storage.first:
#         # logger.info('do_extra_checks: %s' % res)
#         pass
#     _storage.first = False
    return res

def mcdp_dev_warning(s):  # @UnusedVariable
    if user == 'andrea':
        # warnings.warn(s)
        pass

