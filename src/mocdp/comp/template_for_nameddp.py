from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_posets.poset import NotLeq
from mcdp_posets.types_universe import get_types_universe
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
                msg = 'The interface is different.'
                raise_wrapped(DPSemanticError, e, msg, proposed=proposed, v=v)
        
        c = context.child()
        for k, v in self.parameters.items():
            c.var2model[k] = v

        from mcdp_lang.eval_ndp_imp import eval_ndp
        return eval_ndp(self.template_code, c)


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
        msg = 'Different interface'
        raise_desc(DifferentInterface, msg, interface=interface, ndp=ndp)

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













    
