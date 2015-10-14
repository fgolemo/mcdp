from contracts.interface import ContractSyntaxError

class DPInternalError(Exception):
    """ Internal consistency errors (not user) """

class DPUserError(Exception):
    pass


class DPSyntaxError(ContractSyntaxError, DPUserError):
    pass

class DPSemanticError(ContractSyntaxError, DPUserError):
    pass
