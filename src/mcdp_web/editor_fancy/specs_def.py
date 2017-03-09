# -*- coding: utf-8 -*-
from collections import namedtuple

from mcdp_lang.parse_interface import (parse_ndp_eval, parse_ndp_refine,
                                       parse_template_eval, parse_template_refine, parse_constant_eval,
                                       parse_constant_refine, parse_poset_eval, parse_poset_refine)
from mcdp_lang.syntax import Syntax
from mcdp_library import MCDPLibrary

from .image import (get_png_data_model,
                    ndp_template_enclosed, get_png_data_unavailable, get_png_data_poset,
                    get_png_data_syntax_model)
from mcdp.constants import MCDPConstants


Spec = namedtuple('Spec', 
                  ' url_part '
                  ' url_variable'
                  ' extension '
                  ' parse ' # function that returns the object.
                            # It is a composition of the following:
                  ' parse_expr ' #  expr = parse_wrap(string, expr)
                  ' parse_refine ' # expr2 = parse_refine(expr, context)
                  ' parse_eval '   # ndp = parse_eval(expr2, context
                  ' load ' # load(name, context)
                  ' get_png_data'
                  ' get_png_data_syntax'
                  ' write minimal_source_code')
specs = {}

spec_models = specs['models'] = Spec(url_part='models', 
                                     url_variable='model_name',
                      extension=MCDPConstants.ext_ndps,
                      parse=MCDPLibrary.parse_ndp,
                      parse_expr=Syntax.ndpt_dp_rvalue,
                      parse_refine=parse_ndp_refine,
                      parse_eval=parse_ndp_eval,
                      load=MCDPLibrary.load_ndp,
                      get_png_data=get_png_data_model,
                      get_png_data_syntax=get_png_data_syntax_model,
                      write=MCDPLibrary.write_to_model,
                      minimal_source_code="mcdp {\n    \n}")

spec_templates = specs['templates']= Spec(url_part='templates', 
                                          url_variable='template_name',
                      extension=MCDPConstants.ext_templates,
                      parse=MCDPLibrary.parse_template,
                      parse_expr=Syntax.template,
                      parse_refine=parse_template_refine,
                      parse_eval=parse_template_eval,
                      load=MCDPLibrary.load_template,
                      get_png_data=ndp_template_enclosed,
                      get_png_data_syntax=ndp_template_enclosed,
                      write=MCDPLibrary.write_to_template,
                      minimal_source_code="template []\n\nmcdp {\n    \n}")

spec_values = specs['values'] = Spec(url_part='values', 
                                     url_variable='value_name',
                   extension=MCDPConstants.ext_values,
                   parse=MCDPLibrary.parse_constant,
                   parse_expr=Syntax.rvalue,
                   parse_refine=parse_constant_refine,
                   parse_eval=parse_constant_eval,
                   load=MCDPLibrary.load_constant,
                   get_png_data=get_png_data_unavailable,
                   get_png_data_syntax=get_png_data_unavailable,
                   write=MCDPLibrary.write_to_constant,
                   minimal_source_code="0 g")

spec_posets =specs['posets']= Spec(url_part='posets', 
                                   url_variable='poset_name',
                   extension=MCDPConstants.ext_posets,
                   parse=MCDPLibrary.parse_poset,
                   parse_expr=Syntax.space,
                   parse_refine=parse_poset_refine,
                   parse_eval=parse_poset_eval,
                   load=MCDPLibrary.load_poset,
                   get_png_data=get_png_data_poset,
                   get_png_data_syntax=get_png_data_poset,
                   write=MCDPLibrary.write_to_poset,
                   minimal_source_code="poset {\n    \n}")
