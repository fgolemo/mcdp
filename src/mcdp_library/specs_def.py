# -*- coding: utf-8 -*-
from collections import namedtuple

from mcdp.constants import MCDPConstants
from mcdp_dp.primitive import PrimitiveDP
from mcdp_lang.parse_interface import (parse_ndp_eval, parse_ndp_refine,
                                       parse_template_eval, parse_template_refine, parse_constant_eval,
                                       parse_constant_refine, parse_poset_eval, parse_poset_refine,
                                       parse_primitivedp_refine, parse_primitivedp_eval)
from mcdp_lang.syntax import Syntax
from mcdp_library import MCDPLibrary
from mcdp_posets import Poset
from mocdp.comp.context import ValueWithUnits
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.template_for_nameddp import TemplateForNamedDP


# XXX: to revise
def get_png_data_unavailable(*args, **kwargs):
    from mcdp_web.editor_fancy.image import get_png_data_unavailable
    return get_png_data_unavailable(*args, **kwargs)

def get_png_data_model(*args, **kwargs):
    from mcdp_web.editor_fancy.image import get_png_data_model
    return get_png_data_model(*args, **kwargs)

def ndp_template_enclosed(*args, **kwargs):
    from mcdp_web.editor_fancy.image import ndp_template_enclosed
    return ndp_template_enclosed(*args, **kwargs)

def get_png_data_poset(*args, **kwargs):
    from mcdp_web.editor_fancy.image import get_png_data_poset
    return get_png_data_poset(*args, **kwargs)

def get_png_data_syntax_model(*args, **kwargs):
    from mcdp_web.editor_fancy.image import get_png_data_syntax_model
    return get_png_data_syntax_model(*args, **kwargs)




Spec = namedtuple('Spec', 
                  ' klass '
                  ' url_part ' 
                  ' extension '
                  ' parse ' # function that returns the object.
                            # It is a composition of the following:
                  ' parse_expr ' #  expr = parse_wrap(string, expr)
                  ' parse_refine ' # expr2 = parse_refine(expr, context)
                  ' parse_eval '   # ndp = parse_eval(expr2, context
                  ' load ' # load(name, context)
                  ' get_png_data'
                  ' get_png_data_syntax' 
                  ' minimal_source_code'
                  )
specs = {}
SPEC_MODELS = 'models'
SPEC_TEMPLATES = 'templates'
SPEC_VALUES = 'values'
SPEC_POSETS = 'posets'
SPEC_PRIMITIVEDPS = 'primitivedps'

spec_models = specs[SPEC_MODELS] = Spec(url_part=SPEC_MODELS,  
                      klass=NamedDP,
                      extension=MCDPConstants.ext_ndps,
                      parse=MCDPLibrary.parse_ndp,
                      parse_expr=Syntax.ndpt_dp_rvalue,
                      parse_refine=parse_ndp_refine,
                      parse_eval=parse_ndp_eval,
                      load=MCDPLibrary.load_ndp,
                      get_png_data=get_png_data_model,
                      get_png_data_syntax=get_png_data_syntax_model,
                      minimal_source_code="mcdp {\n    \n}")

spec_templates = specs[SPEC_TEMPLATES]= Spec(url_part=SPEC_TEMPLATES,  
                     klass=TemplateForNamedDP,
                      extension=MCDPConstants.ext_templates,
                      parse=MCDPLibrary.parse_template,
                      parse_expr=Syntax.template,
                      parse_refine=parse_template_refine,
                      parse_eval=parse_template_eval,
                      load=MCDPLibrary.load_template,
                      get_png_data=ndp_template_enclosed,
                      get_png_data_syntax=ndp_template_enclosed,
                      minimal_source_code="template []\n\nmcdp {\n    \n}")

spec_values = specs[SPEC_VALUES] = Spec(url_part=SPEC_VALUES, 
                        klass= ValueWithUnits,
                   extension=MCDPConstants.ext_values,
                   parse=MCDPLibrary.parse_constant,
                   parse_expr=Syntax.rvalue,
                   parse_refine=parse_constant_refine,
                   parse_eval=parse_constant_eval,
                   load=MCDPLibrary.load_constant,
                   get_png_data=get_png_data_unavailable,
                   get_png_data_syntax=get_png_data_unavailable,
                   minimal_source_code="0 g")

spec_posets =specs[SPEC_POSETS]= Spec(url_part=SPEC_POSETS,  
                                      klass=Poset,
                   extension=MCDPConstants.ext_posets,
                   parse=MCDPLibrary.parse_poset,
                   parse_expr=Syntax.space,
                   parse_refine=parse_poset_refine,
                   parse_eval=parse_poset_eval,
                   load=MCDPLibrary.load_poset,
                   get_png_data=get_png_data_poset,
                   get_png_data_syntax=get_png_data_poset,
                   minimal_source_code="poset {\n    \n}")
 


spec_primitivedps = specs[SPEC_PRIMITIVEDPS] = Spec(
    klass=PrimitiveDP,
                    url_part=SPEC_PRIMITIVEDPS,  
                   extension=MCDPConstants.ext_primitivedps,
                   parse=MCDPLibrary.parse_primitivedp,
                   parse_expr=Syntax.primitivedp_expr,
                   parse_refine=parse_primitivedp_refine,
                   parse_eval=parse_primitivedp_eval,
                   load=MCDPLibrary.load_primitivedp,
                   get_png_data=get_png_data_unavailable,
                   get_png_data_syntax=get_png_data_unavailable,
                   minimal_source_code="# no example available")

