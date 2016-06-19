from contextlib import contextmanager
from contracts import all_disabled
import sys

class MCDPException(Exception):
    pass

class MCDPExceptionWithWhere(MCDPException):

    def __init__(self, error, where=None):
        self.error = error
        self.where = where
        MCDPException.__init__(self, error, where)

    def __str__(self):
        error, where = self.args
        s = error
        if where is not None:
            from contracts.interface import add_prefix
            s += "\n\n" + add_prefix(where.__str__(), ' ')
        return s

    def with_filename(self, filename):
        """ Returns the same exception with reference
            to the given filename. """
        where = _get_where_with_filename(self, filename)
        return type(self)(self.error, where=where)

class DPInternalError(MCDPExceptionWithWhere):
    """ Internal consistency errors (not user) """

class DPUserError(MCDPExceptionWithWhere):
    """ User mistake """
    pass

class DPSyntaxError(DPUserError):
    pass

class DPSemanticError(DPUserError):
    pass

@contextmanager
def extend_with_filename(realpath):
    try:
        yield
    except MCDPExceptionWithWhere as e:
        _type, _value, traceback = sys.exc_info()
        if realpath is not None:
            e = e.with_filename(realpath)
        else:
            e = e
        raise e, None, traceback

def _get_where_with_filename(e, filename):
    where = e.where
    if where is None:
        print('warning, where is None here: %s' % e)
        where = None
    else:
        where = where.with_filename(filename)
    return where


class _storage:
    first = True

def do_extra_checks():

    res = not all_disabled()
    if _storage.first:
        # logger.info('do_extra_checks: %s' % res)
        pass
    _storage.first = False
    return res

def mcdp_dev_warning(s):
    # warnings.warn(s)
    pass
