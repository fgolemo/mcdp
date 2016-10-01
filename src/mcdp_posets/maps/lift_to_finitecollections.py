from contracts import contract
from mcdp_posets import Map


__all__ = [
    'LiftToFiniteCollections',
]

class LiftToFiniteCollections(Map):

    @contract(f=Map)
    def __init__(self, f):
        from mcdp_posets import FiniteCollectionsInclusion
        dom = FiniteCollectionsInclusion(f.get_domain())
        cod = FiniteCollectionsInclusion(f.get_codomain())
        self.f = f
        Map.__init__(self, dom=dom, cod=cod)

    def _call(self, x):
        elements = x.elements
        elements2 = set(self.f(_) for _ in elements)
        from mcdp_posets import FiniteCollection
        return FiniteCollection(elements2, self.cod)
