from contracts.interface import ContractSyntaxError

class DPInternalError(Exception):
    """ Internal consistency errors (not user) """

class DPUserError(Exception):
    pass


class DPSyntaxError(ContractSyntaxError, DPUserError):
    pass

class DPSemanticError(ContractSyntaxError, DPUserError):
    pass

def do_extra_checks():
    from contracts.enabling import all_disabled
    return all_disabled()

def mcdp_dev_warning(s):
    # warnings.warn(s)
    pass
