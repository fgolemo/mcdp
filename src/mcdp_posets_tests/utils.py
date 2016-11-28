# -*- coding: utf-8 -*-
from contracts.utils import raise_wrapped, raise_desc
from mcdp_posets import NotBelongs


def assert_belongs(space, x):
    try:
        space.belongs(x)
    except NotBelongs as e:
        msg = 'assert_belongs() fails'
        raise_wrapped(Exception, e, msg, space=space, x=x)
        
def assert_does_not_belong(space, x):
    try: 
        space.belongs(x)
    except NotBelongs:
        return
    
    msg = 'assert_does_not_belong() fails: NotBelongs not thrown. '
    raise_desc(AssertionError, msg, space=space, x=x)
    