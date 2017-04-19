
class ViewError(Exception):
    pass

class FieldNotFound(ViewError):
    pass

class EntryNotFound(ViewError, KeyError):
    pass

class InvalidOperation(ViewError):
    pass

class InsufficientPrivileges(ViewError):
    pass