from mcdp_figures.figures_ndp import MakeFiguresNDP
from mcdp_figures.figures_poset import MakeFiguresPoset
from mcdp_posets import FinitePoset
from mcdp_report.gg_ndp import gvgen_from_ndp
from mcdp_report.gg_utils import gg_get_format
from mcdp_web.utils.image_error_catch_imp import create_image_with_string
from mocdp.comp.template_for_nameddp import TemplateForNamedDP
from mcdp.exceptions import mcdp_dev_warning, DPNotImplementedError


def get_png_data_model(image_source, name, thing, data_format, library):  # @UnusedVariable
    mf = MakeFiguresNDP(ndp=thing, image_source=image_source, yourname=name)
    f = 'fancy_editor' 
    res = mf.get_figure(f, data_format)
    return res

def get_png_data_syntax_model(image_source, name, thing, data_format, library):  # @UnusedVariable
    mf = MakeFiguresNDP(ndp=thing, image_source=image_source, yourname=name)
    f = 'ndp_graph_enclosed_TB' 
    res = mf.get_figure(f, data_format)
    return res

# Note this needs also library
def ndp_template_enclosed(image_source, name, thing, data_format, library):
    from mcdp_report.gdc import STYLE_GREENREDSYM

    return ndp_template_graph_enclosed(image_source=image_source, template=thing, style=STYLE_GREENREDSYM, yourname=name,
                                       data_format=data_format, direction='TB', enclosed=True, library=library)

def ndp_template_graph_enclosed(library, template, style, yourname, data_format, direction, enclosed, image_source):
    assert isinstance(template, TemplateForNamedDP)
    mcdp_dev_warning('Wrong - need assume ndp const')

    context = library._generate_context_with_hooks()

    ndp = template.get_template_with_holes(context)

    if enclosed:
        setattr(ndp, '_hack_force_enclose', True)

    gg = gvgen_from_ndp(ndp, style=style, direction=direction,
                        image_source=image_source, yourname=yourname)
    return gg_get_format(gg, data_format)
    
def get_png_data_poset(image_source, name, thing, data_format, library):
    _ = name 
    if isinstance(thing, FinitePoset):
        mf = MakeFiguresPoset(thing, image_source=image_source)
        f = 'hasse_icons' 
        res = mf.get_figure(f, data_format)
        return res
    else:
        return image_from_string(str(thing), data_format) 
        
def create_svg_with_string(x):
    svg="""<svg height="30" width="200">
  <text x="0" y="15" fill="red">Cannot visualize %s</text>
</svg>""" % x
    return svg  

def image_from_string(s, data_format):
    if data_format == 'png':
        return create_image_with_string(s, size=(512, 512), color=(128, 128, 128))
    elif data_format == 'svg':
        return create_svg_with_string(s)
    else:
        raise DPNotImplementedError(data_format)
    
def get_png_data_unavailable(image_source, name, thing, data_format, library):  # @UnusedVariable
    return image_from_string(str(thing), data_format) 
