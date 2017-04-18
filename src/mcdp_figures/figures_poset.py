from contracts import contract
from contracts.utils import check_isinstance

from mcdp_posets import FinitePoset
from mcdp_posets.find_poset_minima.baseline_n2 import poset_minima
from mcdp_report.gdc import choose_best_icon

from .figure_interface import MakeFigures
from .formatters import GGFormatter
from mcdp_report.image_source import NoImages


__all__ = [
    'MakeFiguresPoset',
]


class MakeFiguresPoset(MakeFigures):
    
    def __init__(self, poset, image_source):
        self.poset = poset
        if image_source is None:
            image_source = NoImages()
        self.image_source = image_source
        
        aliases = {
            
        }
        
        figure2function = {
            'hasse': (PosetHasse, dict(direction='TB', icons=False)), 
            'hasse_icons': (PosetHasse, dict(direction='TB', icons=True)),
        }
        
        MakeFigures.__init__(self, aliases=aliases, figure2function=figure2function)
    
    def get_poset(self):
        return self.poset

    def get_image_source(self):
        return self.image_source
            
    

class PosetHasse(GGFormatter):
    
    def __init__(self, direction, icons):
        assert direction in ['LR', 'TB']
        self.direction = direction 
        self.icons = icons

    def get_gg(self, mf):
        poset = mf.get_poset()
        if not isinstance(poset, FinitePoset):
            return ValueError('not available')
         
#         library = mf.get_library()
        image_source = mf.get_image_source()
#         images_paths = library.get_images_paths() if library is not None else []
        import mcdp_report.my_gvgen as gvgen
        gg = gvgen.GvGen(options="rankdir=%s" % self.direction)
        
        e2n = {}
        for e in poset.elements:
            iconoptions = [e]
            icon = choose_best_icon(iconoptions, image_source)
            if icon is not None:
                from mcdp_report.gdc import resize_icon
                resized = resize_icon(icon, 100)

                label = ("<TABLE CELLBORDER='0' BORDER='0'><TR><TD>%s</TD></TR>"
                "<TR><TD><IMG SRC='%s' SCALE='TRUE'/></TD></TR></TABLE>")
                label = label % (e, resized)

            else:
                label = e
            
            n = gg.newItem(label)
            e2n[e] = n
            gg.propertyAppend(n, "shape", "none")
         
         
        for e1, e2 in get_hasse(poset):
            low = e2n[e1]
            high = e2n[e2]
            l = gg.newLink(high, low )
            gg.propertyAppend(l, "arrowhead", "none")
            gg.propertyAppend(l, "arrowtail", "none")
            
        return gg      

@contract(fp=FinitePoset)
def get_hasse(fp):
    """ yiels (a, b) in hasse diagram) """
    check_isinstance(fp, FinitePoset)
    for e1, e2 in fp.relations:
        # check if e2 is minimal
        all_up = set(_ for _ in fp.elements if fp.leq(e1, _) and not fp.leq(_, e1))
    
        minimals = poset_minima(all_up, fp.leq)
        
        if e2 in minimals:
            yield e1, e2
    