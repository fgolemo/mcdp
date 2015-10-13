from contracts import contract
from contracts.utils import raise_wrapped, raise_desc

class InvalidCoords(ValueError):
    pass

@contract(coords='tuple|int|list')
def get_it(seq, coords, reduce_list):
    """
        ['a', ['b', 'c']]
        
        () => ['a', ['b', 'c']]
        [(), ()] => reduce([['a', ['b', 'c']], ['a', ['b', 'c']]])
        [0, (1, 1)] => ['a', 'c']
    
    """
    try:

        if coords == ():
            return seq

        if isinstance(coords, list):
            subs = [get_it(seq, c, reduce_list=reduce_list) for c in coords]
            R = reduce_list(subs)
            return R

        if isinstance(coords, int):
            try:
                return seq[coords]
            except TypeError:
                raise_desc(InvalidCoords, 'Cannot index elemement.', seq=seq, coords=coords)

        assert isinstance(coords, tuple) and len(coords) >= 1, coords
        a = coords[0]
        r = coords[1:]
        if not isinstance(a, int):
            raise_desc(InvalidCoords, 'Expected int', a=a)
        if r:
            s = seq[a]
            assert isinstance(r, tuple)
            return get_it(s, r, reduce_list=reduce_list)
        else:
            assert isinstance(a, int)
            return seq[a]
    except (InvalidCoords, IndexError) as e:
        msg = 'Error while calling %s { %s }' % (seq, coords)
        raise_wrapped(ValueError, e, msg, compact=True,
                      seq=seq, coords=coords, reduce_list=reduce_list)


def simplify_indices(x):
    """ simplifies an index expression """
    if x == [0]:
        return ()
    return x



