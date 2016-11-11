# -*- coding: utf-8 -*-
from contracts.interface import Where
from contracts.utils import raise_desc, raise_wrapped
from mocdp.exceptions import DPInternalError

from .namedtuple_tricks import namedtuplewhere


# Create a type for each length of lists
# with elements e1, e2, e3, etc.
# The list with length 0 has a dummy element "dummy".
list_types = {
}

for i in range(1, 100):
    args = ['e%d' % _ for _ in range(i)]
    ltype = namedtuplewhere('List%d' % i, " ".join(args))
    list_types[i] = ltype

list_types[0] = namedtuplewhere('List0', 'dummy')

def is_a_special_list(x):
    return 'List' in type(x).__name__

def make_list(x, where=None):
    if x is None:
        raise ValueError()
#     if where is None:
#         raise ValueError()
    try:
        if not len(x):
            return list_types[0](dummy='dummy', where=where)

        ltype = list_types[len(x)]
        w1 = x[0].where
        w2 = x[-1].where

        if w1 is None or w2 is None:
            raise_desc(ValueError, 'Cannot create list', x=x)

        assert w2.character_end is not None
        w3 = Where(string=w1.string,
                      character=w1.character,
                      character_end=w2.character_end)

        res = ltype(*tuple(x), where=w3)
        return res
    except BaseException as e:
        msg = 'Cannot create list'
        raise_wrapped(DPInternalError, e, msg, x=x, where=where, x_last=x[-1])

def unwrap_list(res):
    if isinstance(res, list_types[0]):
        return []
    normal = []
    for k, v in res._asdict().items():
        if k == 'where': continue
        normal.append(v)
    return normal


def get_odd_ops(l):
    """ Returns odd elements from l. """
    res = []
    for i, x in enumerate(l):
        if i % 2 == 0:
            res.append(x)
    return res
