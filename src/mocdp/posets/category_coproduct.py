from contracts import contract
from mocdp.posets.space import NotBelongs, NotEqual, Space
from contracts.utils import raise_wrapped, raise_desc


class Coproduct1(Space):
    """
        The coproduct of two spaces A, B
        
        is represented as tuples of the kind
        
        (c, (a, b)) | c \in {0, ..., n-1}  
        
        (0, (a, fill)) | a \in A
        (1, (fill, b)) | b \in B
    
    """
    fill = '-'
    
    @contract(spaces='seq[>=1]($Space)')
    def __init__(self, spaces):
        self.spaces = spaces
        
    def __repr__(self):
        s = "+".join('%s' % sub for sub in self.spaces)
        return "Coproduct1(%s)" % s

    def belongs(self, x):
        try:
            if not isinstance(x, tuple) or not len(x) == 2:
                raise NotBelongs()

            n = len(self.spaces)
            i, s = x
            if not isinstance(i, int) or not 0 <= i <= n - 1:
                raise NotBelongs()

            if not isinstance(s, tuple) or not len(s) == n:
                raise NotBelongs()
            for j, sj in enumerate(s):
                if j == i:
                    try:
                        self.spaces[j].belongs(sj)
                    except NotBelongs as e:
                        msg = 'Element %d' % j
                        raise_wrapped(NotBelongs, e, msg, j=j, sj=sj,
                                      spacej=self.spaces[j])
                else:
                    if not sj == Coproduct1.fill:
                        msg = 'sj is not fill'
                        raise_desc(NotBelongs, msg, sj=sj)
        except NotBelongs as e:
            msg = ''
            raise_wrapped(NotBelongs, e, msg, x=x)
            
    def check_equal(self, a, b):
        try:
            ai, ax = a
            bi, bx = b
            if not ai == bi:
                raise NotBelongs('different index')

            self.spaces[bi].check_equal(ax, bx)
        except NotEqual as e:
            msg = ''
            raise_wrapped(NotEqual, e, msg, a=a, b=b)

    def witness(self):
        import numpy as np
        n = len(self.spaces)
        i = int(np.random.randint(n))
        res = []
        for j in range(n):
            if j == i:
                res.append(self.spaces[j].witness())
            else:
                res.append(Coproduct1.fill)
        return (i, tuple(res))

    def pack(self, i, xi):
        def m(j):
            if j == i:
                return xi
            else:
                return Coproduct1.fill

        res = [m(j) for j in range(len(self.spaces))]
        return i, tuple(res)

    def unpack(self, x):
        """ Returns index, and the active element. """
        i, active = x
        return i, active[i]

    def format(self, x):
        i, e = self.unpack(x)
        return 'alt%s:(%s)' % ((i + 1), self.spaces[i].format(e))

