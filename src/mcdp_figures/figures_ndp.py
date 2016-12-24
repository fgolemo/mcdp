from contracts.utils import raise_wrapped
from mcdp_report.gg_ndp import gvgen_from_ndp
from mocdp import ATTR_LOAD_NAME

from .figure_interface import MakeFigures
from .formatters import MakeFigures_Formatter, TextFormatter, GGFormatter


__all__ = [
    'MakeFiguresNDP',
]

class MakeFiguresNDP(MakeFigures):
    def __init__(self, ndp, library=None, yourname=None):
        self.ndp = ndp
        self.yourname = yourname
        self.library = library
        
        aliases = {
            'ndp_graph_enclosed': 'ndp_graph_enclosed_LR',
            'ndp_graph_expand': 'ndp_graph_expand_LR',
            'ndp_graph_templatized': 'ndp_graph_templatized_LR',
            'ndp_graph_templatized_labeled': 'ndp_graph_templatized_labeled_LR',
            'ndp_graph_normal': 'ndp_graph_normal_LR',
        }
        
        from mcdp_report.gdc import STYLE_GREENREDSYM
        
        figure2function = {
            'fancy_editor': (Enclosed, 
                dict(direction='TB', enclosed=True, style=STYLE_GREENREDSYM, skip_initial=False)),
            'fancy_editor_LR': (Enclosed, 
                dict(direction='LR', enclosed=True, style=STYLE_GREENREDSYM, skip_initial=False)),
            'ndp_graph_enclosed_LR': (Enclosed, 
                dict(direction='LR', enclosed=True, style=STYLE_GREENREDSYM)), 
            'ndp_graph_enclosed_TB': (Enclosed, 
                dict(direction='TB', enclosed=True, style=STYLE_GREENREDSYM)),
            'ndp_graph_expand_LR': (Expand, 
                dict(direction='LR', style=STYLE_GREENREDSYM)), 
            'ndp_graph_expand_TB': (Expand, 
                dict(direction='TB', style=STYLE_GREENREDSYM)),
            'ndp_graph_templatized_LR': (Templatized, 
                dict(direction='LR', style=STYLE_GREENREDSYM, labeled=False)), 
            'ndp_graph_templatized_TB': (Templatized, 
                dict(direction='TB', style=STYLE_GREENREDSYM, labeled=False)),
            'ndp_graph_templatized_labeled_LR': (Templatized, 
                dict(direction='LR', style=STYLE_GREENREDSYM, labeled=True)), 
            'ndp_graph_templatized_labeled_TB': (Templatized, 
                dict(direction='TB', style=STYLE_GREENREDSYM, labeled=True)),
            'ndp_graph_normal_LR': (Normal, 
                dict(direction='LR', style=STYLE_GREENREDSYM)), 
            'ndp_graph_normal_TB': (Normal, 
                dict(direction='TB', style=STYLE_GREENREDSYM)),
            
            'ndp_repr_long': (NDP_repr_long, dict()),
        }
        
        # now add the ones from DP
        from .figures_dp import MakeFiguresDP
        mfdp = MakeFiguresDP(None)
        for alias, x in  mfdp.aliases.items():
            if alias in aliases:
                raise ValueError(alias)
            aliases[alias] = x
        for which, (constructor, params) in mfdp.figure2function.items():
            if which in figure2function:
                raise ValueError(which)
            
            params2 = dict(params)
            params2['constructor'] = constructor
            figure2function[which] = (BridgeFormatter, params2)
            BridgeFormatter(**params2)
        
        MakeFigures.__init__(self, aliases=aliases, figure2function=figure2function)
        
    def get_library(self):
        """ Might return None """
        return self.library
    
    def get_ndp(self):
        return self.ndp
    
    def get_yourname(self):
        return self.yourname

class BridgeFormatter(MakeFigures_Formatter):
    def __init__(self, constructor, **kwargs):
        try:    
            self.dpf = constructor(**kwargs)
        except TypeError as e:
            msg = 'Could not instance %s with params %s' %\
                (constructor, kwargs)
            raise_wrapped(TypeError, e, msg)
    def available_formats(self):
        return self.dpf.available_formats()
    def get(self, mf, formats):
        ndp = mf.get_ndp()
        dp = ndp.get_dp()
        from .figures_dp import MakeFiguresDP
        mf2 = MakeFiguresDP(dp=dp)
        
        return self.dpf.get(mf2, formats)
    
class NDP_repr_long(TextFormatter):
    
    def get_text(self, mf):
        ndp = mf.get_ndp()
        return ndp.repr_long()
    

class Normal(GGFormatter):
    """ This is not enclosed """
    def __init__(self, direction, style):
        self.direction = direction
        self.style = style
        
    def get_gg(self, mf):
        ndp = mf.get_ndp()
        library = mf.get_library()
        yourname = mf.get_yourname()
        
        images_paths = library.get_images_paths() if library else []

        gg = gvgen_from_ndp(ndp, self. style, images_paths=images_paths,
                            yourname=yourname, direction=self.direction,
                            skip_initial=True)
        return gg
    
    
def templatize_children_for_figures(ndp, enclosed):
    from mocdp.comp.composite import CompositeNamedDP
    from mocdp.ndp.named_coproduct import NamedDPCoproduct
    from mocdp.comp.composite_templatize import cndp_templatize_children
    from mocdp.comp.composite_templatize import ndpcoproduct_templatize
    

    if isinstance(ndp, CompositeNamedDP):
        ndp2 = cndp_templatize_children(ndp)
        # print('setting _hack_force_enclose %r' % enclosed)
        if enclosed:
            setattr(ndp2, '_hack_force_enclose', True)
    elif isinstance(ndp, NamedDPCoproduct):
        ndp2 = ndpcoproduct_templatize(ndp)
    else:
        ndp2 = ndp
    return ndp2

class Enclosed(GGFormatter):
    def __init__(self, direction, enclosed, style, skip_initial=True):
        self.direction = direction
        self.enclosed = enclosed
        self.style = style
        self.skip_initial = skip_initial
         
    def get_gg(self, mf):

        ndp = mf.get_ndp()
        
        ndp2 = templatize_children_for_figures(ndp, enclosed=self.enclosed)
        
        library = mf.get_library()
        images_paths = library.get_images_paths() if library is not None else []
        
        # we actually don't want the name on top
        yourname = None  # name
        
        gg = gvgen_from_ndp(ndp2, style=self.style, direction=self.direction,
                            images_paths=images_paths, yourname=yourname,
                            skip_initial=self.skip_initial)
        
        return gg

        
class Templatized(GGFormatter):
    def __init__(self, direction, style, labeled):
        self.direction = direction
        self.style = style
        self.labeled = labeled
         
    def get_gg(self, mf):
        ndp = mf.get_ndp()
        library =mf.get_library()
        
        yourname = None 
        if self.labeled:
            if hasattr(ndp, ATTR_LOAD_NAME):
                yourname = getattr(ndp, ATTR_LOAD_NAME)

        from mocdp.comp.composite_templatize import ndp_templatize
        ndp = ndp_templatize(ndp, mark_as_template=False)
        
        images_paths = library.get_images_paths() if library else []
    
        gg = gvgen_from_ndp(ndp, self.style, yourname=yourname,
                            images_paths=images_paths, direction=self.direction,
                            skip_initial=True)
        return gg

class Expand(GGFormatter):
    def __init__(self, direction, style):
        self.direction = direction
        self.style = style


    def get_gg(self, mf):
        """ This expands the children, forces the enclosure """
        library = mf.get_library()
        images_paths = library.get_images_paths() if library is not None else []
        ndp = mf.get_ndp()
        yourname = None  # name
        gg = gvgen_from_ndp(ndp, style=self.style, direction=self.direction,
                            images_paths=images_paths, yourname=yourname,
                            skip_initial=True)
        return gg
    
    