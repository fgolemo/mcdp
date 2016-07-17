from contracts.utils import raise_wrapped
from mcdp_posets import NotJoinable
from mcdp_posets import Map, MapNotDefinedHere
from mocdp.exceptions import do_extra_checks

__all__ = ['Max1Map']

class Max1Map(Map):
    """
        f -> max(value, f)
    """
    def __init__(self, F, value):
        if do_extra_checks():
            F.belongs(value)

        Map.__init__(self, F, F)
        self.value = value
        self.F = F

    def _call(self, x):
        try:
            r = self.F.join(x, self.value)
        except NotJoinable as e:
            msg = 'Cannot compute join of elements.'
            raise_wrapped(MapNotDefinedHere, e, msg, value=self.value, x=x)
        return r
