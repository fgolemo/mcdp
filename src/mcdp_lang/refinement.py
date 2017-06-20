# -*- coding: utf-8 -*-
from mcdp_lang_utils import Where
from contracts.utils import check_isinstance
from mcdp_lang.utils_lists import get_odd_ops
from mcdp import logger
from mcdp.exceptions import (DPInternalError, DPSemanticError, DPSyntaxError,
)

from .eval_warnings import MCDPWarnings, warn_language
from .namedtuple_tricks import get_copy_with_where
from .namedtuple_tricks import isnamedtuplewhere
from .parts import CDPLanguage
from .utils import isnamedtupleinstance
from .utils_lists import make_list
from .utils_lists import unwrap_list


CDP = CDPLanguage

def apply_refinement(expr, context):
    """ 
        Returns a transformed expr with some changes. 
    
        Might raise DPSemanticError.
        
        It also puts warnings in context.
    """ 
    
    def transform(x, parents):  # @UnusedVariable
        # We actually transform only the CDP.ModelStatements
        if not isinstance(x, CDP.ModelStatements):
            return x
        else:
            line_exprs = unwrap_list(x.statements)
            if not line_exprs:
                return x
            
            si = SemanticInformation()
            line_exprs = infer_types_of_variables(line_exprs, context, si)
            logger.debug('Si: %s' % si)
            transformed = CDP.ModelStatements(make_list(line_exprs), where=x.where)
            
            for cname, cinfo in si.constants.items():
                if not cinfo.where_used:
                    msg = 'Constant "%s" is unused.' % cname
                    warn_language(cinfo.element_defined, 
                                  MCDPWarnings.LANGUAGE_UNUSED_CONSTANT, 
                                  msg, context=context)

            
            return transformed

    return namedtuple_visitor_ext(expr, transform)
     

def move_where(x0, string0, offset, offset_end):
    """ Moves all the references to an offset """
    def move_where_rec(x, parents):  # @UnusedVariable
        assert isnamedtuplewhere(x), type(x)
        w = x.where
        assert string0[offset:offset_end] == w.string
        character = w.character + offset
        character_end = w.character_end + offset
        w2 = Where(string0, character, character_end)
        return get_copy_with_where(x, w2)
    res = namedtuple_visitor_ext(x0, move_where_rec)
    return res

def infer_debug(s):
    # print(s)
    pass
    
class SemanticInformationForEntity(object):
    def __init__(self, element_defined, where_used=[]):
        element_defined.where
        #check_isinstance(where_defined, Where)
        self.element_defined = element_defined
        self.where_used = where_used
#     def __str__(self):
# 
#         return 'SemanticInformationForEntity('
        
    def add_use(self, where):
        check_isinstance(where, Where)
        self.where_used.append(where)
        
class SemanticInformation(object):
    def __init__(self):
        # maps str to SemanticInformationForEntity
        self.resources = {}  
        self.functions = {} 
        self.uncertain_constants = {}
        self.constants = {} 
        self.variables = {}
        self.deriv_resources = {}
        self.deriv_functions = {}
        self.instances = {}
        
    def __str__(self):
        return self.summary()
    
    def summary(self):
        s = "SemanticInformation:"
        p = '\n - '
        s += p + 'Resources: %s' % self.resources
        s += p + 'Functions: %s' % self.functions
        s += p + 'Uncertain constants: %s' % self.uncertain_constants
        s += p + 'Constants: %s' % self.constants
        s += p + 'Variables: %s' % self.variables
        s += p + 'Deriv resources: %s' % self.deriv_resources
        s += p + 'Deriv functions: %s' % self.deriv_functions
        s += p + 'Instances: %s' % self.instances
        return s
        
    def found_constant(self, name, element):
        check_isinstance(name, str)
        where = element.where
        infer_debug('found constant: %s' % name)
        if name in self.constants:
            msg = 'Duplicated constants?'
            raise DPInternalError(msg, where=where)  # XXX
        self.constants[name] = SemanticInformationForEntity(element) 
    
    def found_uncertain_constant(self, name, element):
        check_isinstance(name, str)
        where = element.where
        infer_debug('found uncertain constant: %s' % name)
        if name in self.constants: # XXX
            msg = 'Duplicated constants?'
            raise DPInternalError(msg, where=where) 
        self.uncertain_constants[name] = SemanticInformationForEntity(element) 
    
    def is_constant(self, name):
        check_isinstance(name, str)
        return name in self.constants
    
    def constant_mark_used(self, name, element):
        where = element.where
        self.constants[name].add_use(where)
        
    def found_instance(self, name, element):
        check_isinstance(name, str)
        where = element.where
        if name in self.instances:
            msg = 'Duplicated instances?'
            raise DPInternalError(msg, where=where) 
        self.instances[name] = SemanticInformationForEntity(element) 
        
def infer_types_of_variables(line_exprs, context, si):
    check_isinstance(si, SemanticInformation)

    # These are the resources and functions defined by the model
    resources = set()
    functions = set()
    variables = set()
    # These are new derived resources and functions
    deriv_resources = set()
    deriv_functions = set()
    
    def found_fname(fname):
        if isinstance(fname, CDP.Placeholder):
            return
        check_isinstance(fname, CDP.FName)
        infer_debug('found fname: %s' % fname.value)
        _ = fname.value
        if _ in functions:
            msg = 'Repeated function %r.' % _
            raise DPSemanticError(msg, where=fname.where)
        
        if _ in deriv_resources:
            msg = 'The name %r is already used.' % _
            raise DPSemanticError(msg, where=fname.where)

        if _ in variables:
            msg = 'The name %r is already used by a variable.' % _
            raise DPSemanticError(msg, where=fname.where)

        functions.add(fname.value)
    
    def found_rname(rname):
        if isinstance(rname, CDP.Placeholder):
            return

        check_isinstance(rname, CDP.RName)
        _ = rname.value
        if _ in resources:
            msg = 'Repeated resource %r.' % _
            raise DPSemanticError(msg, where=rname.where)
        
        if _ in deriv_resources:
            msg = 'The name %r is already used.' % _
            raise DPSemanticError(msg, where=rname.where)

        if _ in variables:
            msg = 'The name %r is already used by a variable.' % _
            raise DPSemanticError(msg, where=rname.where)
            
        resources.add(rname.value) 
    
    def found_vname(vname):
        check_isinstance(vname, CDP.VName) 
        variables.add(vname.value)

    def is_constant(vref):
        check_isinstance(vref, CDP.VariableRef)
        it_is = si.is_constant(vref.name) 
        return it_is
    
    def check_all_constant(rvalue):
        """ Checks that all VariableRefs are constant """
        class Tmp():
            verified = True
        def visit_to_check(x, parents):  # @UnusedVariable
            assert isnamedtuplewhere(x), type(x)
            not_allowed = CDP.FName, CDP.RName, CDP.UncertainRes, CDP.UncertainFun
            if isinstance(x, not_allowed):
                Tmp.verified = False
            if isinstance(x, CDP.VariableRef):
                if not is_constant(x):
                    Tmp.verified = False
                else:
                    pass
            return x
        namedtuple_visitor_ext(rvalue, visit_to_check)
        return Tmp.verified
    
    UNDEFINED, FVALUE, RVALUE, CONFLICTING, EITHER =\
     'undefined', 'fvalue', 'rvalue', 'conflicting', 'either' 

    def get_flavour(xx):
        class Flavors:
            fvalue = set()
            rvalue = set()
            undefined = set()
            either = set()
            
        def visit_to_check2(x):
#             print('  visit_to_check2(%s)  %s %s' % (nt_string(x), type(x).__name__, x))
            if isinstance(x, CDP.Resource):
                l = x.dp.value + '.' + x.s.value
                Flavors.rvalue.add(l)
            elif isinstance(x, CDP.Function):
                l = x.dp.value + '.' + x.s.value
                Flavors.fvalue.add(l) 
            elif isinstance(x, CDP.VName):
                Flavors.either.add(x.value)
            elif isinstance(x, CDP.VariableRef):
                if x.name in functions and x.name in resources:
                    # ambiguous
                    Flavors.either.add(x.name) # not other flavor  
                elif x.name in functions or x.name in deriv_resources:
#                     print('%r contributes to Flavors.rvalue' % x.name)
                    Flavors.rvalue.add(x.name) # not other flavor
                elif x.name in resources or x.name in deriv_functions:
#                     print('%r contributes to Flavors.fvalue' % x.name)
                    Flavors.fvalue.add(x.name) # not other flavor
                elif x.name in variables:
#                     print('%r contributes to Flavors.either' % x.name)
                    Flavors.either.add(x.name)  
                elif si.is_constant(x.name):
#                     print('%r constant contributes to Flavors.either' % x.name)
                    Flavors.either.add(x.name)  
                else:
                    msg = 'Could not resolve reference to %r.' % x.name
                    raise DPSemanticError(msg, where=x.where)
            
        namedtuple_visitor_only_visit(xx, visit_to_check2)
        
        infer_debug('Results of %r: rv %s;  fv %s;  undef %s; either %s' % (
            nt_string(rvalue), Flavors.rvalue, Flavors.fvalue, Flavors.undefined,
            Flavors.either))
        if Flavors.rvalue and Flavors.fvalue:
            return CONFLICTING
        if Flavors.undefined:
            return UNDEFINED
        if Flavors.rvalue and Flavors.fvalue:
            return CONFLICTING
        if not Flavors.rvalue and Flavors.fvalue:
            return FVALUE
        if not Flavors.fvalue and Flavors.rvalue:
            return RVALUE
        return EITHER
            
    def can_be_treated_as_rvalue(x):
        res = get_flavour(x)
        infer_debug('Results of %r -> %s' % (nt_string(x), res))
        return res in [RVALUE, EITHER] 
    
    def can_be_treated_as_fvalue(x):
        res = get_flavour(x)
        infer_debug('Results of %r -> %s' % (nt_string(x), res))
        return res in [FVALUE, EITHER]
     
    for i, l in enumerate(line_exprs):
        infer_debug('\n\n--- line %r (%s)' % ( 
            l.where.string[l.where.character:l.where.character_end], type(l)))
        from .syntax import Syntax
        # mark functions, resources, variables, and constants
        if isinstance(l, CDP.SetNameNDPInstance):
            si.found_instance(l.name.value, l.name)
        elif isinstance(l, (CDP.FunStatement, CDP.FunShortcut1, CDP.FunShortcut2)):
            found_fname(l.fname)
        elif isinstance(l, (CDP.ResStatement, CDP.ResShortcut1, CDP.ResShortcut2)):
            found_rname(l.rname)
        elif isinstance(l, (#CDP.ResShortcut4, 
                            CDP.ResShortcut5,
                            CDP.ResShortcut1m)):
            for _ in get_odd_ops(unwrap_list(l.rnames)):
                found_rname(_)
        elif isinstance(l, (#CDP.FunShortcut4, 
                            CDP.FunShortcut5,
                            CDP.FunShortcut1m)):
            for _ in get_odd_ops(unwrap_list(l.fnames)):
                found_fname(_)
        
        if isinstance(l, CDP.SetNameConstant):
            si.found_constant(l.name.value, l)
        
        if isinstance(l, CDP.SetNameUncertainConstant):
            si.found_uncertain_constant(l.name.value, l)
            
        if isinstance(l, CDP.VarStatement):
            for _ in get_odd_ops(unwrap_list(l.vnames)):
                found_vname(_)
            
        if isinstance(l, CDP.FunShortcut2):
            pass
        elif isinstance(l, CDP.ResShortcut2):
            rvalue = l.rvalue
        elif isinstance(l, CDP.SetNameRValue):
            # first of all, chech if all the references on the right 
            # are constant. 
            rvalue = l.right_side
            all_constant = check_all_constant(rvalue)
            if all_constant:
                # This can become simply a constant
                infer_debug('The value %r can be recognized as constant' % str(l.name.value))
                si.found_constant(l.name.value, l)
            else:
            # This is a special case, because it is the place
            # where the syntax is ambiguous.
            #  
            #     x = Nat: 1 + r
            #  
            # could be interpreted with r being a functionality
            # or a resource.
            #  
            # By default it is parsed as SetNameRValue, and so we get here.
                try:
                    w = l.where
                    s = w.string[w.character:w.character_end]
                    from .parse_actions import parse_wrap
                    alt0 = parse_wrap(Syntax.setname_fvalue, s)[0]
                    assert isinstance(alt0, CDP.SetNameFValue), alt0
                    alt = move_where(alt0, w.string, w.character, w.character_end)
                except DPSyntaxError as _:
                    #print "No, it does not parse: %s" % traceback.format_exc(e)
                    alt = None
                    
                if alt:
                    #logger.info('Ambiguous')
                    # both are feasible; check covariance
                    one_ok = can_be_treated_as_rvalue(l.right_side)
                    two_ok = can_be_treated_as_fvalue(alt.right_side)
#                    print('can be rvalue %s fvalue %s' % (one_ok, two_ok))

                    if (not one_ok) and (not two_ok):
                        msg = ('This expression cannot be interpreted either'
                              ' as a functionality or as a resource.')
                        raise DPSemanticError(msg, where=l.right_side.where)

                    if one_ok and two_ok:
                        if isinstance(l.right_side, CDP.UncertainRes):
                            msg = ('This expression is ambiguous. I will interpret it as a resource.')
                            warn_language(l.right_side, 
                                          MCDPWarnings.LANGUAGE_AMBIGUOS_EXPRESSION, 
                                          msg, context=context)
                            deriv_resources.add(l.name.value)
                        else:
                            msg = ('This expression is truly ambiguous, and I cannot '
                                  'judge whether it is a functionality or resource.')
                            e = DPSemanticError(msg, where=l.right_side.where)
                            raise e
                                
                    elif one_ok and not two_ok:
                        # we have concluded this can be a rvalue
                        #print('setting %r as deriv_resources' % l.name.value)
                        deriv_resources.add(l.name.value)
                        
                    elif two_ok and not one_ok:
                        #print('setting %r as deriv_functions' % l.name.value)
                        deriv_functions.add(l.name.value)
                        # we replace the line
                        line_exprs[i] = alt
                else:
                    #  print('setting %r as deriv_resources' % l.name.value)
                    deriv_resources.add(l.name.value)

        elif isinstance(l, CDP.SetNameFValue):
            deriv_functions.add(l.name.value)
        elif isinstance(l, CDP.SetNameConstant):
            pass
        elif isinstance(l, (CDP.FunStatement, CDP.ResStatement)):
            pass
        else:
            #  print('line %s' % type(l).__name__)
            pass
    
    refine0 = lambda x, parents: refine(x, parents, si, None, resources, functions, 
                                        variables, deriv_resources, deriv_functions,
                                        context=context)
    
    line_exprs = [namedtuple_visitor_ext(_, refine0) for _ in line_exprs]
    
    return line_exprs



def nt_string(x):
    assert isnamedtuplewhere(x)
    w = x.where
    res = w.string[w.character:w.character_end]
    return res


def namedtuple_visitor_only_visit(x, visit):
    def transform(x, parents):  # @UnusedVariable
        visit(x)
        return x
    namedtuple_visitor_ext(x, transform)
    
    
def namedtuple_visitor_ext(x, transform, parents=None):
    """ It's not a visitor ... """
    if parents is None:
        parents = ()
        
    # special case: only useful when parsing 1.0 floatnumber
    # otherwise we do not get here because of (x) below
    if isinstance(x, (int, float, str)):
        return x
    
    assert isnamedtupleinstance(x), x
    
    d = x._asdict()
    for k, v in d.items():
        if isnamedtupleinstance(v):
            parents2 = parents + ( (x, k),  )
            v2 = namedtuple_visitor_ext(v, transform, parents=parents2)
        else: # (x)
            v2 = v
         
        d[k] = v2
    
    T = type(x)
    x1 = T(**d)

    if isnamedtuplewhere(x1):
        x1 = transform(x1, parents=parents)

    return x1

def refine(x, parents, si,
           _constants, resources, functions, variables, deriv_resources,
           deriv_functions, context):
    
    is_rvalue_context = any(k == 'rvalue' for _, k in parents)
    is_fvalue_context = any(k == 'fvalue' for _, k in parents)
    
    assert not (is_rvalue_context and is_fvalue_context)
    
    if isinstance(x, CDP.VariableRef):
        if si.is_constant(x.name):
            cname = CDP.CName(x.name, where=x.where)
            res = CDP.ConstantRef(cname=cname, where=x.where)
            si.constant_mark_used(x.name, x)
            return res
        elif x.name in resources and x.name in functions:
            if is_fvalue_context:
                msg = 'Please use "required %s" rather than just "%s".' % (x.name, x.name)
                warn_language(x, MCDPWarnings.LANGUAGE_REFERENCE_OK_BUT_IMPRECISE, msg, context)

                # interpret as 
                return CDP.NewResource(None, 
                                       CDP.RName(x.name, where=x.where), 
                                   where=x.where)
            if is_rvalue_context:
                msg = 'Please use "provided %s" rather than just "%s".' % (x.name, x.name)
                warn_language(x, MCDPWarnings.LANGUAGE_REFERENCE_OK_BUT_IMPRECISE, msg, context)

                return CDP.NewFunction(None, 
                                       CDP.FName(x.name, where=x.where), 
                                       where=x.where)
                
            msg = 'I cannot say whether %r refers to the functionality or resource.' % x.name
            msg += ' Need to implement >= - aware refinement.'
            warn_language(x, MCDPWarnings.LANGUAGE_AMBIGUOS_EXPRESSION, msg, context)
            return x
        
        elif x.name in resources:
            if x.name in variables:
                msg = 'I cannot say whether "%s" refers to the variable or resource.' % x.name
                warn_language(x, MCDPWarnings.LANGUAGE_AMBIGUOS_EXPRESSION, msg, context)
                return x 
            
            msg = 'Please use "required %s" rather than just "%s".' % (x.name, x.name)
            warn_language(x, MCDPWarnings.LANGUAGE_REFERENCE_OK_BUT_IMPRECISE, msg, context)

            return CDP.NewResource(None, CDP.RName(x.name, where=x.where), where=x.where)

        elif x.name in functions:
            if x.name in variables:
                msg = 'I cannot say whether "%s" refers to the variable or functionality.' % x.name
                warn_language(x, MCDPWarnings.LANGUAGE_AMBIGUOS_EXPRESSION, msg, context) # XXX
                return x
            
            msg = 'Please use "provided %s" rather than just "%s".' % (x.name, x.name)
            warn_language(x, MCDPWarnings.LANGUAGE_REFERENCE_OK_BUT_IMPRECISE, msg, context) # XXX

            return CDP.NewFunction(None, CDP.FName(x.name, where=x.where), where=x.where) 

        elif x.name in deriv_resources:
            where = x.where
            drname = CDP.DerivResourceName(x.name, where=where)
            res = CDP.DerivResourceRef(drname, where=where)
            return res

        elif x.name in deriv_functions:
            # XXX: this is not correct
            where = x.where
            dfname = CDP.DerivFunctionName(x.name, where=where)
            res = CDP.DerivFunctionRef(dfname, where=where)
            return res
        
        elif x.name in variables:
            where = x.where
            dfname = CDP.VName(x.name, where=where)
            res = CDP.ActualVarRef(dfname, where=where)
            return res
        else:
            msg = 'I cannot judge this VariableRef: %r' % str(x)
            logger.error(msg)
            # raise DPInternalError(msg)
   
    if isinstance(x, CDP.SetNameGenericVar):
        if si.is_constant(x.value):
            return CDP.CName(x.value, where=x.where)

        elif x.value in deriv_resources:
            # XXX: this is not correct
            return CDP.RName(x.value, where=x.where)

        elif x.value in deriv_functions:
            # XXX: this is not correct
            return CDP.FName(x.value, where=x.where)
        else:
            
            logger.error('I cannot judge this SetNameGenericVar: %r' % str(x))
    return x