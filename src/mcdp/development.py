# -*- coding: utf-8 -*-
import getpass

from contracts import all_disabled

from mcdp_utils_misc import memoize_simple


# import warnings
@memoize_simple
def get_user():
    return getpass.getuser()
# class _storage:
#     first = True

def do_extra_checks():
    """ True if we want to do extra paranoid checks for functions. """
    res = not all_disabled()
#     if _storage.first:
#         # logger.info('do_extra_checks: %s' % res)
#         pass
#     _storage.first = False
    return res


def mcdp_dev_warning(s):  # @UnusedVariable
    if get_user() in  ['andrea']:
        #warnings.warn(s)
        pass


