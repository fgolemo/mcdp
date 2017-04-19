# -*- coding: utf-8 -*-
from mcdp_lang.eval_warnings import warn_language, MCDPWarnings
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.refinement import SemanticInformation, infer_types_of_variables
from mcdp_lang.utils_lists import unwrap_list
from mocdp.comp.interfaces import NotConnected


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
                        
