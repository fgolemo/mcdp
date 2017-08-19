import os


def expand_all(x0):
    x = x0
    x = os.path.expanduser(x)
    x = os.path.expandvars(x)
    if '$' in x:
        msg = 'Cannot resolve all environment variables in %r.' % x0
        raise ValueError(msg)
    return x
