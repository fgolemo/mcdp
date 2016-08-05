from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_posets import NotLeq, get_types_universe
from mocdp.exceptions import DPSemanticError

__all__ = [
    'TemplateForNamedDP'
]

class TemplateForNamedDP():

    @contract(parameters='dict(str:isinstance(NamedDP))')
    def __init__(self, parameters, template_code):
        """
        
        """
        self.parameters = parameters
        self.template_code = template_code

    @contract(parameter_assignment='dict(str:isinstance(NamedDP))')
    def specialize(self, parameter_assignment, context):
        
        for k, v in self.parameters.items():
            if not k in parameter_assignment:
                msg = 'Parameter not specified.'
                raise_desc(DPSemanticError, msg, missing=k)
            
            proposed = parameter_assignment[k]
            try:
                check_same_interface(v,  proposed)
            except DifferentInterface as e:
                msg = 'Cannot specialize the template because the interface is different.'
                raise_wrapped(DPSemanticError, e, msg,
                              interface=describe_interface(v),
                              proposed=describe_interface(proposed),
                              compact=True)
        
        c = context.child()
        for k, v in parameter_assignment.items():
            c.var2model[k] = v

        from mcdp_lang.eval_ndp_imp import eval_ndp
        return eval_ndp(self.template_code, c)
    
    
    def get_template_with_holes(self):
        """ Returns a CompositeNamedDP with special "Hole" nodes. """
        from mocdp.comp.context import Context
        from mocdp.comp.composite_templatize import ndp_templatize

        context = Context()

        parameters = dict(**self.parameters)
        for k in parameters:
            # mark_as_template makes it use a special class that
            # is then recognized by gg_ndp and plotted as dashed
            p = ndp_templatize(parameters[k], mark_as_template=True)
            setattr(p, 'template_parameter', k)
            parameters[k] = p


        return self.specialize(parameters, context)


class DifferentInterface(Exception):
    pass

def check_same_interface(interface, ndp):
    """ Raises DifferentInterface """
    
    fi = set(interface.get_fnames())
    ri = set(interface.get_rnames())
    fn = set(ndp.get_fnames())
    rn = set(ndp.get_rnames())
    
    extra_functions = fn - fi
    extra_resources = rn - ri
    missing_functions = fi - fn
    missing_resources = ri - rn
     
    problems = (extra_functions 
                 or extra_resources 
                 or missing_functions 
                 or missing_resources)
    
    if problems:
        msg = 'Different number of functions and resources.'
        raise_desc(DifferentInterface, msg)


    tu = get_types_universe()

    for f in ndp.get_fnames():
        F1 = ndp.get_ftype(f)
        F2 = interface.get_ftype(f)
        try:
            tu.check_leq(F1, F2)
        except NotLeq as e:
            msg = 'A port is not compatible.'
            raise_desc(DPSemanticError, e, msg, f=f, F1=F1, F2=F2)

    for r in ndp.get_rnames():
        R1 = ndp.get_rtype(r)
        R2 = interface.get_rtype(r)
        try:
            tu.check_leq(R1, R2)
        except NotLeq as e:
            msg = 'A port is not compatible.'
            raise_desc(DPSemanticError, e, msg, r=r, R1=R1, R2=R2)


def describe_interface(ndp):
    fnames = ndp.get_fnames()
    ftypes = ndp.get_ftypes(fnames)
    rnames = ndp.get_rnames()
    rtypes = ndp.get_rtypes(rnames)
    return "fnames: %s\nftypes: %s\nrnames: %s\nrtypes: %s" % (fnames, ftypes, rnames, rtypes)










    
