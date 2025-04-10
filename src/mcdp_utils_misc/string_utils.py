# -*- coding: utf-8 -*-

def get_md5(contents):
    """
    Compute the MD5 hash of the given content.
    
    In Python 3, hash functions require bytes, so we convert strings to bytes if needed.
    
    Args:
        contents: The content to hash (string or bytes)
        
    Returns:
        str: The hexadecimal digest of the hash
    """
    import hashlib
    m = hashlib.md5()
    
    # Convert to bytes if it's a string
    if isinstance(contents, str):
        contents = contents.encode('utf-8')
    
    m.update(contents)
    s = m.hexdigest()
    return s

def get_sha1(contents):
    """
    Compute the SHA1 hash of the given content.
    
    In Python 3, hash functions require bytes, so we convert strings to bytes if needed.
    
    Args:
        contents: The content to hash (string or bytes)
        
    Returns:
        str: The hexadecimal digest of the hash
    """
    import hashlib
    m = hashlib.sha1()
    
    # Convert to bytes if it's a string
    if isinstance(contents, str):
        contents = contents.encode('utf-8')
    
    m.update(contents)
    s = m.hexdigest()
    return s


def format_list(items):
    """
    Returns a nicely formatted list as a string.
    
    Args:
        items: The list to format
        
    Returns:
        str: A formatted string representation of the list
    """
    if not items:
        return '(empty)'
    else:
        # Use f-strings for more readable formatting in Python 3
        return ", ".join(f'"{item}"' for item in items)