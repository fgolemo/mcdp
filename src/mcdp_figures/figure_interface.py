from abc import ABCMeta, abstractmethod
import sys  

from contracts import contract
from contracts.utils import check_isinstance, raise_desc, raise_wrapped
from mcdp_report.gg_utils import gg_get_formats


__all__ = [
    'MakeFiguresNDP',
]

class MakeFiguresNDP():
    
    def __init__(self, ndp, library=None, yourname=None):
        self.ndp = ndp
        self.yourname = yourname
        self.library = library
        
        self.aliases = {
            'ndp_graph_enclosed': 'ndp_graph_enclosed_LR',
        }
        
        from mcdp_report.gdc import STYLE_GREENREDSYM
        
        self.figure2function = {
            'ndp_graph_enclosed_LR': (Enclosed, 
                dict(direction='LR', enclosed=True, style=STYLE_GREENREDSYM)), 
            'ndp_graph_enclosed_TB': (Enclosed, 
                dict(direction='TB', enclosed=True, style=STYLE_GREENREDSYM)),  
        }
        
    def available(self):
        return set(self.figure2function)
    
    def available_formats(self, name):
        if not name in self.available():
            raise ValueError(name)
        k, p = self.figure2function[name]
        formatter = k(**p)
        return formatter.available_formats()
    
    def get_library(self):
        """ Might return None """
        return self.library
    
    def get_ndp(self):
        return self.ndp
    
    def get_yourname(self):
        return self.yourname
    
    @contract(name=str, formats='str|seq(str)')
    def get_figure(self, name, formats, **params):
        """ Returns a dictionary format_name -> bytes """
        if name in self.aliases:
            name = self.aliases['name']
        
        if not name in self.figure2function:
            msg = 'Invalid figure %r.' % name
            raise ValueError(msg)
        
        k, p0 = self.figure2function[name]
        p = dict()
        p.update(p0)
        p.update(params)
        
        try:
            formatter = k(**p)
        except Exception as e:
            msg = 'Cannot instantiate %r with params %r.' % (name, p)
            raise_wrapped(Exception, e, msg, params=p, exc=sys.exc_info() )
             
        check_isinstance(formatter, MakeFiguresNDP_Formatter)
        
        formats = (formats,) if isinstance(formats, str) else tuple(sorted(formats))
        
        available = formatter.available_formats()
        
        for _f in formats:
            if not _f in available:
                msg = 'Format %s not provided.' % _f
                raise_desc(ValueError, msg, available=available)
                
        res = formatter.get(self, formats)
        
        if not isinstance(res, tuple) and len(res) == len(formats):
            msg = 'Invalid result of %s' % name
            raise_desc(ValueError, msg, res=res)
        
        r = dict(zip(formats, res))

        return r
    
class MakeFiguresNDP_Formatter():
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def available_formats(self):
        """ Returns a set of formats that are available """
    
    @abstractmethod    
    def get(self, mf, formats):
        """
            mf: MakeFiguresNDP
            formats: tuple of strings
            
            must return a tuple of same length as formats
        """

class Enclosed(MakeFiguresNDP_Formatter):
    def __init__(self, direction, enclosed, style):
        self.direction = direction
        self.enclosed = enclosed
        self.style = style
        
    def available_formats(self):
        return ['png', 'pdf', 'svg', 'dot']

    def get(self, mf, formats):
        from mocdp.comp.composite import CompositeNamedDP
        from mocdp.ndp.named_coproduct import NamedDPCoproduct
        from mocdp.comp.composite_templatize import cndp_templatize_children
        from mocdp.comp.composite_templatize import ndpcoproduct_templatize
        from mcdp_report.gg_ndp import gvgen_from_ndp

        ndp = mf.get_ndp()
        
        if isinstance(ndp, CompositeNamedDP):
            ndp2 = cndp_templatize_children(ndp)
            # print('setting _hack_force_enclose %r' % enclosed)
            if self.enclosed:
                setattr(ndp2, '_hack_force_enclose', True)
        elif isinstance(ndp, NamedDPCoproduct):
            ndp2 = ndpcoproduct_templatize(ndp)
        else:
            ndp2 = ndp
    
        library = mf.get_library()
        images_paths = library.get_images_paths() if library is not None else []
        
        # we actually don't want the name on top
        yourname = None  # name
        gg = gvgen_from_ndp(ndp2, style=self.style, direction=self.direction,
                            images_paths=images_paths, yourname=yourname)
    
        res = gg_get_formats(gg, formats)
        return res
    
    