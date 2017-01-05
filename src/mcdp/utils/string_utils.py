
def get_md5(contents):
    import hashlib
    m = hashlib.md5()
    m.update(contents)
    s = m.hexdigest()
    return s