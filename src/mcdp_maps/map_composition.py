from contracts import contract
from mcdp_posets.space import Map
from mocdp.exceptions import mcdp_dev_warning


class MapComposition(Map):

    """ Composition of a series of maps """

    @contract(maps='seq(Map)')
    def __init__(self, maps):
        self.maps = tuple(maps)

        mcdp_dev_warning('Check that the composition makes sense')
        dom = self.maps[0].get_domain()
        cod = self.maps[-1].get_codomain()
        Map.__init__(self, dom=dom, cod=cod)

    def _call(self, x):
        res = x
        for m in self.maps:
            res = m.__call__(res)
        return res
