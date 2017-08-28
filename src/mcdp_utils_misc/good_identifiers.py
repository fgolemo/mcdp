
import re
from mcdp.constants import MCDPConstants
r_identifier = re.compile(r"^[^\d\W]\w*\Z")


    
def is_good_plain_identifier(x):
    m = re.match(r_identifier, x)
    return m is not None

def assert_good_plain_identifier(x, for_what=None):
    if MCDPConstants.softy_mode:
        return
    if not is_good_plain_identifier(x):
        if for_what is not None:
            msg = 'This is not a good identifier for %s: "%s".' % (for_what, x)
        else:
            msg = 'This is not a good identifier: "%s".' % x
        raise ValueError(msg)
    