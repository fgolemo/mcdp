# -*- coding: utf-8 -*-
from .space import NotBelongs, NotEqual, Space
from contracts import contract
from contracts.utils import check_isinstance, indent, raise_desc

__all__ = [
    'SpaceProduct',
]


class SpaceProduct(Space):
    """ A product of Posets with the product order. """
    @contract(subs='seq($Space)')
    def __init__(self, subs):
        assert isinstance(subs, tuple)
        self.subs = subs

    def __len__(self):
        return len(self.subs)

    def __getitem__(self, index):
        check_isinstance(index, int)
        return self.subs[index]

    def check_equal(self, a, b):
        problems = []
        for i, (sub, x, y) in enumerate(zip(self.subs, a, b)):
            try:
                sub.check_equal(x, y)
            except NotEqual as e:
                msg = '#%d (%s): %s ≰ %s.' % (i, sub, x, y)
                msg += '\n' + indent(str(e).strip(), '| ')
                problems.append(msg)
        if problems:
            msg = 'Equal does not hold.\n'
            msg = "\n".join(problems)
            raise_desc(NotEqual, msg, args_first=False, self=self, a=a, b=b)

    def belongs(self, x):
        if not isinstance(x, tuple):
            raise_desc(NotBelongs, 'Not a tuple', x=x, self=self)
        if not len(x) == len(self.subs):
            raise_desc(NotBelongs, 'Length does not match: len(x) = %s != %s'
                       % (len(x), len(self.subs)),
                        x=x, self=self)

        problems = []
        for i, (sub, xe) in enumerate(zip(self.subs, x)):
            try:
                sub.belongs(xe)
            except NotBelongs as e:
                msg = '#%s: Component %s does not belong to factor %s' % (i, xe, sub)
                msg += '\n' + indent(str(e).strip(), '| ')
                problems.append(msg)

        if problems:
            msg = 'The point does not belong to this product space.\n'
            msg += "\n".join(problems)
            raise_desc(NotBelongs, msg, args_first=False, self=self, x=x)

    def format(self, x):
        if not isinstance(x, tuple):
            raise_desc(NotBelongs, 'Not a tuple', x=x, self=self)

        ss = []
        for _, (sub, xe) in enumerate(zip(self.subs, x)):
            label = getattr(sub, 'label', '_')
            if not label or label[0] == '_':
                s = sub.format(xe)
            else:
                s = '%s:%s' % (label, sub.format(xe))
            ss.append(s)

    # 'MATHEMATICAL LEFT ANGLE BRACKET' (U+27E8) ⟨
    # 'MATHEMATICAL RIGHT ANGLE BRACKET'   ⟩

        return '⟨' + ', '.join(ss) + '⟩'

    def witness(self):
        return tuple(x.witness() for x in self.subs)

    def __repr__(self):
        def f(x):
            if hasattr(x, '__mcdplibrary_load_name'):
                return getattr(x, '__mcdplibrary_load_name')

            r = x.__repr__()
            if  r[-1] != ')' and (isinstance(x, SpaceProduct) or ("×" in r)):
                return "(%s)" % r
            else:
                return r

        if len(self.subs) == 0:
            return "𝟙"
            # return "1"

        if len(self.subs) == 1:
            return '(%s×)' % f(list(self.subs)[0])

        return "×".join(map(f, self.subs))

    def __eq__(self, other):
        return isinstance(other, SpaceProduct) and other.subs == self.subs
