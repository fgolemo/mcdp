# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets import Map, PosetProduct
from mcdp_posets import SpaceProduct
from mcdp.exceptions import mcdp_dev_warning


__all__ = [
    'SpaceProductMap',
    'PosetProductMap',
]

# 
class SpaceProductMap(Map):
    @contract(fs='seq[>=1]($Map)')
    def __init__(self, fs):
        fs = tuple(fs)
        self.fs = fs
        mcdp_dev_warning('add promotion to SpaceProduct')
        dom = SpaceProduct(tuple(fi.get_domain() for fi in fs))
        cod = SpaceProduct(tuple(fi.get_codomain() for fi in fs))
        Map.__init__(self, dom=dom, cod=cod)
 
    def _call(self, x):
        x = tuple(x)
        return tuple(fi(xi) for fi, xi in zip(self.fs, x))


class PosetProductMap(Map):
    @contract(fs='seq[>=1]($Map)')
    def __init__(self, fs):
        fs = tuple(fs)
        self.fs = fs
        mcdp_dev_warning('add promotion to SpaceProduct')
        dom = PosetProduct(tuple(fi.get_domain() for fi in fs))
        cod = PosetProduct(tuple(fi.get_codomain() for fi in fs))
        Map.__init__(self, dom=dom, cod=cod)

    def _call(self, x):
        x = tuple(x)
        return tuple(fi(xi) for fi, xi in zip(self.fs, x))

    def repr_map(self, letter):  # @UnusedVariable
        letters = [letter + '%d' % i for i in range(len(self.fs))]
        def make_tuple(x):
            return "<" + ",".join(x) + ">"
        first = make_tuple(letters)
        seconds = []
        for i, f in enumerate(self.fs):
            x = f.repr_map(letters[i])
            si = x.split('⟼')[1].strip()
            seconds.append(si)
        second = make_tuple(seconds)
        s = '{} ⟼ {}'.format(first, second)
        return s
        