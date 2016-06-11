from contracts import ContractSyntaxError, all_disabled

class DPInternalError(Exception):
    """ Internal consistency errors (not user) """

class DPUserError(Exception):
    """ User mistake """
    pass

class DPSyntaxError(ContractSyntaxError, DPUserError):

    def with_filename(self, filename):
        """ Returns the same exception with reference
            to the given filename. """
        where = _get_where_with_filename(self, filename)
        return type(self)(self.error, where=where)

class DPSemanticError(ContractSyntaxError, DPUserError):

    def with_filename(self, filename):
        """ Returns the same exception with reference
            to the given filename. """
        where = _get_where_with_filename(self, filename)
        return type(self)(self.error, where=where)

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
