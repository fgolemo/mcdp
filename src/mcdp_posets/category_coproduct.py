from .space import NotBelongs, NotEqual, Space
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
import random

__all__ = [
    'Coproduct1',
    'Coproduct1Labels'
]

class Coproduct1(Space):
    """
        The coproduct of spaces A, B, ..
        
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
        if not (isinstance(x, tuple) and len(x) == 2 and isinstance(x[0], int)):
            msg = 'This is not a valid element.'
            raise_desc(ValueError, msg, x=x, self=self)
        i, active = x
        return i, active[i]

    def format(self, x):
        i, e = self.unpack(x)
        return 'alt%s:(%s)' % ((i + 1), self.spaces[i].format(e))


class Coproduct1Labels(Space):
    """
        The coproduct of spaces A, B, ... with a set of labels.
        
        It is represented as tuples of the kind
        
        (label, (a, b, c))   
        
        ('l1', (a, fill, fill)) | a \in A
        ('l2', (fill, b, fill)) | b \in B
    
    """
    fill = '-'

    @contract(spaces='seq[N,>=1]($Space)', labels='seq[N](str)')
    def __init__(self, spaces, labels):
        self.spaces = spaces
        if len(set(labels)) < len(labels):
            msg = 'Invalid argument "labels".'
            raise_desc(ValueError, msg, labels=labels)
        self.labels = labels

    def __repr__(self):
        s = "+".join('%s:%s' % (l, sub) for l, sub in zip(self.labels, self.spaces))
        return "Coproduct1Labels(%s)" % s

    def belongs(self, x):
        try:
            if not isinstance(x, tuple) or not len(x) == 2:
                raise NotBelongs()

            n = len(self.spaces)
            label, s = x
            if not label in self.labels:
                msg = 'Unknown label.'
                raise_desc(NotBelongs, msg, label=label, labels=self.labels)

            if not isinstance(s, tuple) or not len(s) == n:
                raise NotBelongs()

            i = self.labels.index(label)

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

            i = self.labels.index(ai)
            self.spaces[i].check_equal(ax, bx)
        except NotEqual as e:
            msg = ''
            raise_wrapped(NotEqual, e, msg, a=a, b=b)

    def witness(self):
        n = len(self.spaces)
        i = int(random.randint(0, n - 1))
        res = []
        for j in range(n):
            if j == i:
                res.append(self.spaces[j].witness())
            else:
                res.append(Coproduct1.fill)
        label = self.labels[i]
        return (label, tuple(res))

    def pack(self, label, xi):
        if not label in self.labels:
            msg = 'The label is not allowed.'
            raise_desc(ValueError, msg, label=label)
        i = self.labels.index(label)
        def m(j):
            if j == i:
                return xi
            else:
                return Coproduct1.fill

        res = [m(j) for j in range(len(self.spaces))]
        return label, tuple(res)

    @contract(returns='tuple(int, *)')
    def unpack(self, x):
        """ Returns index, and the active element. """
        if not (isinstance(x, tuple) and len(x) == 2):
            msg = 'This is not a valid element.'
            raise_desc(ValueError, msg, x=x, self=self)
        label, active = x
        i = self.labels.index(label) 
        return i, active[i]

    def format(self, x):
        i, e = self.unpack(x)
        return 'alt%s(%s):(%s)' % ((i + 1), self.labels[i], self.spaces[i].format(e))
