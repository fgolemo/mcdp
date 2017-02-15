# -*- coding: utf-8 -*-
import cgi
from collections import defaultdict, namedtuple
import json
import os

from bs4 import BeautifulSoup
from pyramid.httpexceptions import HTTPFound  # @UnresolvedImport
from pyramid.renderers import render_to_response  # @UnresolvedImport

from contracts import contract
from contracts.utils import check_isinstance, raise_desc
from mcdp import logger
from mcdp.exceptions import DPInternalError, DPSemanticError, DPSyntaxError
from mcdp.utils.timing import timeit_wall
from mcdp_lang.eval_warnings import warn_language, MCDPWarnings
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.refinement import SemanticInformation, infer_types_of_variables
from mcdp_lang.suggestions import get_suggestions, apply_suggestions
from mcdp_lang.syntax import Syntax
from mcdp_lang.utils_lists import unwrap_list
from mcdp_library import MCDPLibrary
from mcdp_report.html import ast_to_html, ATTR_WHERE_CHAR, ATTR_WHERE_CHAR_END
from mcdp_web.editor_fancy.image import get_png_data_model, \
    ndp_template_enclosed, get_png_data_unavailable, get_png_data_poset,\
    get_png_data_syntax_model
from mcdp_web.utils import (ajax_error_catch,
                            format_exception_for_ajax_response, response_image)
from mcdp_web.utils.response import response_data
from mcdp_web.utils0 import add_other_fields
from mocdp.comp.interfaces import NamedDP, NotConnected


from mcdp_lang.parse_interface import( parse_ndp_eval, parse_ndp_refine, 
    parse_template_eval, parse_template_refine, parse_constant_eval, 
    parse_constant_refine, parse_poset_eval, parse_poset_refine)


__all__ = ['generate_unconnected_warnings']

def generate_unconnected_warnings(ndp, context0, x):
    CDP = CDPLanguage
    
    if isinstance(x, CDP.BuildProblem):
        si = SemanticInformation()
        line_exprs = unwrap_list(x.statements.statements)
        infer_types_of_variables(line_exprs, context0, si)
        try:
            ndp.check_fully_connected()
        except NotConnected as e:
            if hasattr(e, 'unconnected_fun'):
                ufs = e.unconnected_fun
                urs = e.unconnected_res
                
                for uf in ufs:
                    if uf.dp in si.instances:    
                        msg = 'Unconnected function “%s”.' % uf.s
                        element = si.instances[uf.dp].element_defined
                        which = MCDPWarnings.UNCONNECTED_FUNCTION
                        warn_language(element, which, msg, context0)
    
                for ur in urs:
                    if ur.dp in si.instances:
                        msg = 'Unconnected resource “%s”.' % ur.s
                        element = si.instances[ur.dp].element_defined
                        which = MCDPWarnings.UNCONNECTED_RESOURCE 
                        warn_language(element, which, msg, context0)
                        
