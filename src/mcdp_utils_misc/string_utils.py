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