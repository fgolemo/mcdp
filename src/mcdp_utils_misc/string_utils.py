# -*- coding: utf-8 -*-

def get_md5(contents):
    import hashlib
    m = hashlib.md5()
    m.update(contents)
    s = m.hexdigest()
    return s

def get_sha1(contents):
    import hashlib
    m = hashlib.sha1()
    m.update(contents)
    s = m.hexdigest()
    return s


def format_list(l):
    """ Returns a nicely formatted list. """
    if not l:
        return '(empty)'
    else:
        return ", ".join( '"%s"' % _.__str__() for _ in l)