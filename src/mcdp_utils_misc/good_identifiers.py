
import re
r_identifier = re.compile(r"^[^\d\W]\w*\Z")


    
def is_good_plain_identifier(x):
    m = re.match(r_identifier, x)
    return m is not None

def assert_good_plain_identifier(x, for_what=None):
    if not is_good_plain_identifier(x):
        if for_what is not None:
            msg = f"This is not a good identifier for {for_what}: {x!r}"
        else:
            msg = 'This is not a good identifier: "%s".' % x
        raise ValueError(msg)
    