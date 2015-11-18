from contracts import ContractSyntaxError, all_disabled

class DPInternalError(Exception):
    """ Internal consistency errors (not user) """

class DPUserError(Exception):
    pass

class DPSyntaxError(ContractSyntaxError, DPUserError):

    def with_filename(self, filename):
        where = self.where.with_filename(filename)
        return type(self)(self.error, where=where)

class DPSemanticError(ContractSyntaxError, DPUserError):
    def with_filename(self, filename):
        where = self.where.with_filename(filename)
        return type(self)(self.error, where=where)

class _storage:
    first = True

def do_extra_checks():

    res = not all_disabled()
    if _storage.first:
        print('do_extra_checks: %s' % res)
    _storage.first = False
    return res

def mcdp_dev_warning(s):
    # warnings.warn(s)
    pass
