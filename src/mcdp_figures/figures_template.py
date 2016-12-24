from .figure_interface import MakeFigures
from .formatters import GGFormatter


__all__ = [
    'MakeFiguresTemplate',
]

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
                dict(direction='LR', enclosed=True, style=STYLE_GREENREDSYM, templatize_children=False)), 
            'template_graph_enclosed_TB': (EnclosedTemplate, 
                dict(direction='TB', enclosed=True, style=STYLE_GREENREDSYM, templatize_children=False)),
            'template_children_summarized_LR': (EnclosedTemplate, 
                dict(direction='LR', enclosed=True, style=STYLE_GREENREDSYM, templatize_children=True)), 
            'template_children_summarized_TB': (EnclosedTemplate, 
                dict(direction='TB', enclosed=True, style=STYLE_GREENREDSYM, templatize_children=True)),
        }

        MakeFigures.__init__(self, aliases=aliases, figure2function=figure2function)
        
    def get_template(self):
        return self.template
    
    def get_library(self):
        """ Might return None """
        return self.library
    
    def get_yourname(self):
        return self.yourname


class EnclosedTemplate(GGFormatter):
    def __init__(self, direction, enclosed, style, templatize_children):
        self.direction = direction
        self.enclosed = enclosed
        self.style = style
        self.templatize_children = templatize_children
         
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

        if self.templatize_children:
            from mcdp_figures.figures_ndp import templatize_children_for_figures
            ndp = templatize_children_for_figures(ndp, enclosed=self.enclosed)


        if self.enclosed:
            setattr(ndp, '_hack_force_enclose', True)
    
        images_paths = library.get_images_paths()
        gg = gvgen_from_ndp(ndp, style=self.style, direction=self.direction,
                            images_paths=images_paths, yourname=yourname,
                            skip_initial=True)
    
        return gg
    
    