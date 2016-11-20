from abc import ABCMeta, abstractmethod
import inspect
import sys  

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_report.gg_utils import gg_get_formats
from mocdp import ATTR_LOAD_NAME


__all__ = [
    'MakeFiguresNDP',
]

class MakeFigures():
    def __init__(self, aliases, figure2function):
        self.aliases = aliases
        self.figure2function = figure2function
        
    def available(self):
        return set(self.figure2function) | set(self.aliases)
    def available_unique(self):
        return set(self.figure2function)
    def available_formats(self, name):
        if not name in self.available():
            raise ValueError(name)
        
        if name in self.aliases:
            name = self.aliases[name]
        k, p = self.figure2function[name]
        try:
            formatter = k(**p)
        except TypeError as e:
            msg = 'Could not instance formatter'
            raise_wrapped(TypeError, e, msg, k=k, p=p, name=name)
        return formatter.available_formats()
    
    
    @contract(name=str, formats='str|seq(str)')
    def get_figure(self, name, formats, **params):
        """ If formats is a str, returns a str.
            If formats is a seq, returns a dictionary format_name -> bytes 
        """
        if name in self.aliases:
            name = self.aliases[name]
        
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
             
#         check_isinstance(formatter, MakeFiguresNDP_Formatter)
        
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

        if len(formats) == 0:
            return res[formats[0]]
        
        return r
    
class MakeFiguresTemplate(MakeFigures):
    def __init__(self, template, library=None, yourname=None):
        self.template = template
        self.yourname = yourname
        self.library = library
        
        aliases = {
            'template_graph_enclosed': 'template_graph_enclosed_LR',
        }
        
        from mcdp_report.gdc import STYLE_GREENREDSYM
        
        figure2function = {
            'template_graph_enclosed_LR': (EnclosedTemplate, 
                dict(direction='LR', enclosed=True, style=STYLE_GREENREDSYM)), 
            'template_graph_enclosed_TB': (EnclosedTemplate, 
                dict(direction='TB', enclosed=True, style=STYLE_GREENREDSYM)),

        }

        MakeFigures.__init__(self, aliases=aliases, figure2function=figure2function)
        
    def get_template(self):
        return self.template
    
    def get_library(self):
        """ Might return None """
        return self.library
    
    def get_yourname(self):
        return self.yourname


    
class MakeFiguresDP(MakeFigures):
    def __init__(self, dp):
        self.dp = dp
        
        aliases = {
            'dp_graph_flow': 'dp_graph_flow_TB',
            'dp_graph_tree': 'dp_graph_tree_TB',
            'dp_graph_tree_compact': 'dp_graph_tree_compact_TB',
        }
        
        figure2function = {
            'dp_graph_flow_LR': (DPGraphFlow, dict(direction='LR')), 
            'dp_graph_flow_TB': (DPGraphFlow, dict(direction='TB')),
            'dp_graph_tree_LR': (DPGraphTree, dict(direction='LR', compact=False)), 
            'dp_graph_tree_TB': (DPGraphTree, dict(direction='TB', compact=False)),
            'dp_graph_tree_compact_LR': (DPGraphTree, dict(direction='LR', compact=True)), 
            'dp_graph_tree_compact_TB': (DPGraphTree, dict(direction='TB', compact=True)),
            'dp_repr_long': (DP_repr_long, dict()),
        }
        
        MakeFigures.__init__(self, aliases=aliases, figure2function=figure2function)
    
    def get_dp(self):
        return self.dp
    
                   
class MakeFigures_Formatter():
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
        mf2 = MakeFiguresDP(dp=dp)
        return self.dpf.get(mf2, formats)
    
class TextFormatter(MakeFigures_Formatter):
    def available_formats(self):
        return ['txt']
    
    def get(self, mf, formats):
        assert len(formats) == 1, formats        
        text = self.get_text(mf)
        return (text,)
    
    @abstractmethod
    def get_text(self, mf):
        pass

class NDP_repr_long(TextFormatter):
    
    def get_text(self, mf):
        ndp = mf.get_ndp()
        return ndp.repr_long()
    
class DP_repr_long(TextFormatter):
    
    def get_text(self, mf):
        dp = mf.get_dp()
        return dp.repr_long()
    
class GGFormatter(MakeFigures_Formatter):

    def available_formats(self):
        return ['png', 'pdf', 'svg', 'dot']
    
    def get(self, mf, formats):
        gg = self.get_gg(mf)
        res = gg_get_formats(gg, formats)
        return res
    
    @abstractmethod
    def get_gg(self, mf):
        pass

class Expand(GGFormatter):
    def __init__(self, direction, style):
        self.direction = direction
        self.style = style

    def available_formats(self):
        return ['png', 'pdf', 'svg', 'dot']

    def get_gg(self, mf):
        """ This expands the children, forces the enclosure """
        library = mf.get_library()
        images_paths = library.get_images_paths() if library is not None else []
        ndp = mf.get_ndp()
        yourname = None  # name
        from mcdp_report.gg_ndp import gvgen_from_ndp
        gg = gvgen_from_ndp(ndp, style=self.style, direction=self.direction,
                            images_paths=images_paths, yourname=yourname)
        return gg
            
class Templatized(GGFormatter):
    def __init__(self, direction, style, labeled):
        self.direction = direction
        self.style = style
        self.labeled = labeled
         
        
    def get_gg(self, mf):
        ndp = mf.get_ndp()
        library =mf.get_library()
        # yourname = mf.get_yourname()
        
        yourname = None 
        if self.labeled:
            if hasattr(ndp, ATTR_LOAD_NAME):
                yourname = getattr(ndp, ATTR_LOAD_NAME)

        from mocdp.comp.composite_templatize import ndp_templatize
        ndp = ndp_templatize(ndp, mark_as_template=False)
        
        images_paths = library.get_images_paths() if library else []
    
        from mcdp_report.gg_ndp import gvgen_from_ndp
        gg = gvgen_from_ndp(ndp, self.style, yourname=yourname,
                            images_paths=images_paths, direction=self.direction)
        return gg

class Normal(GGFormatter):
    """ This is not enclosed """
    def __init__(self, direction, style):
        self.direction = direction
        self.style = style
        
    def get_gg(self, mf):
        ndp = mf.get_ndp()
        library =mf.get_library()
        yourname = mf.get_yourname()
        
        images_paths =  library.get_images_paths() if library else []
        from mcdp_report.gg_ndp import gvgen_from_ndp

        gg = gvgen_from_ndp(ndp, self. style, images_paths=images_paths,
                            yourname=yourname, direction=self.direction)
        return gg
    
class Enclosed(GGFormatter):
    def __init__(self, direction, enclosed, style):
        self.direction = direction
        self.enclosed = enclosed
        self.style = style
         
    def get_gg(self, mf):
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
    
        return gg
    
    
class EnclosedTemplate(GGFormatter):
    def __init__(self, direction, enclosed, style):
        self.direction = direction
        self.enclosed = enclosed
        self.style = style
         
    def get_gg(self, mf):
        from mcdp_report.gg_ndp import gvgen_from_ndp

        template = mf.get_template()
        library = mf.get_library()
        yourname = mf.get_yourname()
        
        if library is not None:
            context = library._generate_context_with_hooks()
        else:
            from mocdp.comp.context import Context
            context = Context()
    
        ndp = template.get_template_with_holes(context)
    
        if self.enclosed:
            setattr(ndp, '_hack_force_enclose', True)
    
        images_paths = library.get_images_paths()
        gg = gvgen_from_ndp(ndp, style=self.style, direction=self.direction,
                            images_paths=images_paths, yourname=yourname)
    
        return gg
    
class DPGraphFlow(GGFormatter):
    def __init__(self, direction):
        self.direction = direction
        
    def get_gg(self, mf):
        dp = mf.get_dp()
        from mcdp_report.dp_graph_flow_imp import dp_graph_flow
        gg = dp_graph_flow(dp, direction=self.direction)
        return gg
    
class DPGraphTree(GGFormatter):
    def __init__(self, compact, direction):
        self.compact = compact
        self.direction = direction
        
    def get_gg(self, mf):
        dp = mf.get_dp()
        from mcdp_report.dp_graph_tree_imp import dp_graph_tree
        gg = dp_graph_tree(dp, imp=None, compact=self.compact, direction=self.direction)
        return gg
