
from .imp import get_it

def compose_indices(A, i1, i2, reducel):
#     print('A: %s ' % str(A))
#     print('i1: %s ' % str(i1))
#     print('i2: %s ' % str(i2))

    i0 = get_id_indices(A)
#     print('i0: %s' % str(i0))
    i0i1 = get_it(i0, i1, reducel)
#     print('i0i1: %s' % str(i0i1))
    i0i1i2 = get_it(i0i1, i2, reducel)
#     print('i0i1i2: %s' % str(i0i1i2))
    return i0i1i2

        
def get_id_indices(x, prefix=None):
    if prefix is None:
        prefix = ()

    if is_iterable(x):
        return [ get_id_indices(m, prefix=prefix + (i,))
                for i, m in enumerate(x)]

    if len(prefix) == 1:
        return prefix[0]

    return prefix



def is_iterable(x):
    if isinstance(x, str):
        return False

    try:
        iter(x)
    except TypeError:
        return False
    else:
        return True