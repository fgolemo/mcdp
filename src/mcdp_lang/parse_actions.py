# -*- coding: utf-8 -*-
from contextlib import contextmanager
import sys
import traceback

from decorator import decorator

from contracts import contract
from contracts.interface import Where
from contracts.utils import indent, raise_desc, raise_wrapped, check_isinstance
from mocdp import logger
from mocdp.exceptions import (DPInternalError, DPSemanticError, DPSyntaxError,
    MCDPExceptionWithWhere, do_extra_checks, mcdp_dev_warning)

from .namedtuple_tricks import get_copy_with_where
from .parts import CDPLanguage
from .pyparsing_bundled import ParseException, ParseFatalException
from .utils import isnamedtupleinstance, parse_action
from .utils_lists import make_list, unwrap_list
from mcdp_lang.namedtuple_tricks import recursive_print, isnamedtuplewhere
from mcdp_lang.pyparsing_bundled import Word, printables
from mcdp_lang.eval_warnings import MCDPWarnings, warn_language



CDP = CDPLanguage
 

@decorator
def decorate_add_where(f, *args, **kwargs):
    where = args[0].where
    try:
        return f(*args, **kwargs)
    except MCDPExceptionWithWhere as e:
        _, _, tb = sys.exc_info()
        raise_with_info(e, where, tb)


@contextmanager
def add_where_information(where):
    """ Adds where field to DPSyntaxError or DPSemanticError thrown by code. """
    active = True
    if not active:
        logger.debug('Note: Error tracing disabled in add_where_information().')
        
    if not active:
        mcdp_dev_warning('add_where_information is disabled')
        yield
    else:
        try:
            yield
        except MCDPExceptionWithWhere as e:
            mcdp_dev_warning('add magic traceback handling here')
            _, _, tb = sys.exc_info()
            raise_with_info(e, where, tb)


def nice_stack(tb):
    lines = traceback.format_tb(tb)
    # remove contracts stuff
    lines = [_ for _ in lines if not '/src/contracts' in _]
    s = "".join(lines)
    import os
    curpath = os.path.realpath(os.getcwd())
    s = s.replace(curpath, '.')
    return s
    

def raise_with_info(e, where, tb):
    check_isinstance(e, MCDPExceptionWithWhere)
    existing = getattr(e, 'where', None)
    if existing: 
        raise
    use_where = existing if existing is not None else where
    error = e.error
    
    stack = nice_stack(tb)
    
    args = (error, use_where, stack)
    raise type(e), args, tb

def wheredecorator(b):
    def bb(tokens, loc, s):
        where = Where(s, loc)
        try:
            res = b(tokens)
        except DPSyntaxError as e:
            if e.where is None:
                e.where = where
                raise DPSyntaxError(str(e), where=where)
            else:
                raise
        except DPSemanticError as e:
            if e.where is None:
                raise DPSemanticError(str(e), where=where)
            else:
                raise
        except BaseException as e:
            raise_wrapped(DPInternalError, e, "Error while parsing.",
                          where=where.__str__(), tokens=tokens)

        if isnamedtupleinstance(res) and res.where is None:
            res = get_copy_with_where(res, where=where)

        return res
    return bb

def spa(x, b): 
    bb = wheredecorator(b)
    @parse_action
    def p(tokens, loc, s):
        # print('parsing %r %r %r ' % (tokens, loc, s))
        res = bb(tokens, loc, s)
        # if we are here, then it means the parse was succesful
        # we try again to get loc_end
        character_end = x.tryParse(s, loc)
        
        if isnamedtupleinstance(res) and \
            (res.where is None or res.where.character_end is None):
            w2 = Where(s, character=loc, character_end=character_end)
            res = get_copy_with_where(res, where=w2)

        if do_extra_checks():
            if not isinstance(res, (float, int, str)):
                if res.where is None:
                    msg = 'Found element with no where'
                    raise_desc(ValueError, msg, res=res)

            if hasattr(res, 'where'):
                assert res.where.character_end is not None, \
                    (res, isnamedtupleinstance(res))

        return res
    x.setParseAction(p)

@parse_action
def dp_model_statements_parse_action(tokens):
    line_exprs = list(tokens)
    line_exprs = infer_types_of_variables(line_exprs)
        
    return CDP.ModelStatements(make_list(line_exprs))

def move_where(x0, string0, offset, offset_end):
    """ Moves all the references to an offset """
    def move_where_rec(x):
        assert isnamedtuplewhere(x), type(x)
        w = x.where
        assert string0[offset:offset_end] == w.string
        character = w.character + offset
        character_end = w.character_end + offset
        w2 = Where(string0, character, character_end)
        return get_copy_with_where(x, w2)
    res = namedtuple_visitor(x0, move_where_rec)
    return res

def infer_types_of_variables(line_exprs):
    constants = set()
    # These are the resources and functions defined by the model
    resources = set()
    functions = set()
    variables = set()
    # These are new derived resources and functions
    deriv_resources = set()
    deriv_functions = set()
    
    def found_fname(fname):
        check_isinstance(fname, CDP.FName)
#         print('found fname: %s' % fname.value)
        if fname.value in functions:
            msg = 'Repeated function %r.' % fname.value
            raise DPSemanticError(msg, where=fname.where)
        functions.add(fname.value)
    
    def found_rname(rname):
        check_isinstance(rname, CDP.RName)
#         print('found rname: %s' % rname.value)
        if rname.value in resources:
            msg = 'Repeated resource %r.' % rname.value
            raise DPSemanticError(msg, where=rname.where)
        resources.add(rname.value)

    def found_cname(cname):
        check_isinstance(cname, CDP.CName)
#         print('found constant: %s' % cname.value)
        if cname.value in constants:
            msg = 'Duplicated constants?'
            raise DPInternalError(msg, where=cname.where) 
        constants.add(cname.value) 
        
    def found_vname(vname):
        check_isinstance(vname, CDP.VName)
#         print('found variable: %s' % vname.value)
        # TODO: check not already exists
        variables.add(vname.value)

    def is_constant(vref):
        check_isinstance(vref, CDP.VariableRef)
        it_is =  vref.name in constants
#         if it_is:
#             print('     [yes, %r is constant]' % vref.name)
        return it_is
    
    def check_all_constant(rvalue):
        """ Checks that all VariableRefs are constant """
        class Tmp:
            verified = True
        def visit_to_check(x):
            assert isnamedtuplewhere(x), type(x)
#             w = x.where
#             s = w.string[w.character:w.character_end]
#             print('   visit_to_check %r (%s)' % (s, type(x).__name__))
            not_allowed = CDP.FName, CDP.RName
            if isinstance(x, not_allowed):
                Tmp.verified = False
            if isinstance(x, CDP.VariableRef):
                if not is_constant(x):
                    Tmp.verified = False
                else:
                    pass
#                     print('   variable ref %s is a constant' % str(x))
            return x
        namedtuple_visitor(rvalue, visit_to_check)
        return Tmp.verified
    
    UNDEFINED, FVALUE, RVALUE, CONFLICTING, EITHER =\
     'undefined', 'fvalue', 'rvalue', 'conflicting', 'either'
#     flavors = [UNDEFINED, FVALUE, RVALUE, CONFLICTING, EITHER]

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
#             elif isinstance(x, CDP.FName):
# #                 print('%r (FName) contributes to Flavors.rvalue' % x.name)
#                 Flavors.rvalue.add(x.value)
#             elif isinstance(x, CDP.RName):
# #                 print('%r (RName) contributes to Flavors.fvalue' % x.name)
#                 Flavors.fvalue.add(x.value)
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
                elif x.name in constants:
#                     print('%r constant contributes to Flavors.either' % x.name)
                    Flavors.either.add(x.name)  
                else:
                    msg = 'Could not resolve reference to %r.' % x.name
                    raise DPSemanticError(msg, where=x.where)
            
        namedtuple_visitor_only_visit(xx, visit_to_check2)
        
        print('Results of %r: rv %s fv %s undef %s either %s' % (
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
        print 'Results of %r -> %s' % (nt_string(x), res)
        return res in [RVALUE, EITHER] 
    
    def can_be_treated_as_fvalue(x):
        res = get_flavour(x)
        print 'Results of %r -> %s' % (nt_string(x), res)
        return res in [FVALUE, EITHER]
     
    for i, l in enumerate(line_exprs):
        print('\n\n--- line %r (%s)' % ( 
            l.where.string[l.where.character:l.where.character_end], type(l)))
        print recursive_print(l)
        from mcdp_lang.syntax import Syntax
        # mark functions, resources, variables, and constants
        if isinstance(l, (CDP.FunStatement, CDP.FunShortcut1, CDP.FunShortcut2)):
            found_fname(l.fname)
        elif isinstance(l, (CDP.ResStatement, CDP.ResShortcut1, CDP.ResShortcut2)):
            found_rname(l.rname)
        elif isinstance(l, (#CDP.ResShortcut4, 
                            CDP.ResShortcut1m)):
            for _ in unwrap_list(l.rnames):
                found_rname(_)
        elif isinstance(l, (#CDP.FunShortcut4, 
                            CDP.FunShortcut1m)):
            for _ in unwrap_list(l.fnames):
                found_fname(_)
        
        if isinstance(l, CDP.SetNameConstant):
            found_cname(l.name)
            
        if isinstance(l, CDP.VarStatement):
            for _ in unwrap_list(l.vnames):
                found_vname(_)
            
        if isinstance(l, CDP.FunShortcut2):
#             fvalue = l.lf
            pass
        elif isinstance(l, CDP.ResShortcut2):
            rvalue = l.rvalue
#             print recursive_print(l)
        elif isinstance(l, CDP.SetNameRValue):
            # first of all, chech if all the references on the right 
            # are constant. 
            rvalue = l.right_side
            all_constant = check_all_constant(rvalue)
            if all_constant:
                # This can become simply a constant
#                 print('The value %r can be recognized as constant' % str(l.name.value))
                constants.add(l.name.value)
            
            else:
                """"
                This is a special case, because it is the place
                where the syntax is ambiguous.
                
                    x = Nat: 1 + r
                
                could be interpreted with r being a functionality
                or a resource.
                
                By default it is parsed as SetNameRValue, and so we get here.
                """
                try:
                    w = l.where
                    s = w.string[w.character:w.character_end]
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
                        msg = ('This expression is truly ambiguous, and I cannot '
                              'judge whether it is a functionality or resource.')
                        e = DPSemanticError(msg, where=l.right_side.where)
                        raise e
                                
                    if one_ok and not two_ok:
                        # we have concluded this can be a rvalue
                        #print('setting %r as deriv_resources' % l.name.value)
                        deriv_resources.add(l.name.value)
                        
                    if two_ok and not one_ok:
                        #print('setting %r as deriv_functions' % l.name.value)
                        deriv_functions.add(l.name.value)
                        # we replace the line
                        line_exprs[i] = alt
                else:
#                     print('setting %r as deriv_resources' % l.name.value)
                    deriv_resources.add(l.name.value)

        elif isinstance(l, CDP.SetNameFValue):
#             fvalue = l.right_side
            deriv_functions.add(l.name.value)
        elif isinstance(l, CDP.SetNameConstant):
            pass
        elif isinstance(l, (CDP.FunStatement, CDP.ResStatement)):
            pass
        else:
#             print('line %s' % type(l).__name__)
            pass
    
    def refine(x):
        if isinstance(x, CDP.VariableRef):
            if x.name in constants:
                cname = CDP.CName(x.name, where=x.where)
                res = CDP.ConstantRef(cname=cname, where=x.where)
                return res
            elif x.name in resources and x.name in functions:
                msg = 'I cannot say whether %r refers to the functionality or resource.' % x.name
                msg += ' Need to implement >= - aware refinement.'
                warn_language(x, MCDPWarnings.LANGUAGE_AMBIGUOS_EXPRESSION, msg, context=None) # XXX
                return x
            elif x.name in resources:
                if x.name in variables:
                    msg = 'I cannot say whether %r refers to the variable or resource.' % x.name
                    warn_language(x, MCDPWarnings.LANGUAGE_AMBIGUOS_EXPRESSION, msg, context=None) # XXX
                    return x 
                
                return CDP.NewResource(None, CDP.RName(x.name, where=x.where), 
                                       where=x.where)
 
            elif x.name in functions:
                if x.name in variables:
                    msg = 'I cannot say whether %r refers to the variable or functionality.' % x.name
                    warn_language(x, MCDPWarnings.LANGUAGE_AMBIGUOS_EXPRESSION, msg, context=None) # XXX
                    return x
                
                return CDP.NewFunction(None, CDP.FName(x.name, where=x.where), 
                                       where=x.where) 

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
            if x.value in constants:
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
        
    line_exprs = [namedtuple_visitor(_, refine) for _ in line_exprs]
    
    for l in line_exprs:
        print recursive_print(l)
    return line_exprs

def nt_string(x):
    assert isnamedtuplewhere(x)
    w = x.where
    res = w.string[w.character:w.character_end]
    return res

def namedtuple_visitor_only_visit(x, visit):
    def transform(x):
        visit(x)
        return x
    namedtuple_visitor(x, transform)
    
def namedtuple_visitor(x, transform):
    if not isnamedtupleinstance(x):
        raise_desc(ValueError,'?', type=type(x).__name__, x=x)
    
    d = x._asdict()
    for k, v in d.items():
        if isnamedtupleinstance(v):
            v2 = namedtuple_visitor(v, transform)
        else:
            v2 = v
         
        d[k] = v2
    
    T = type(x)
    x1 = T(**d)

    if isnamedtuplewhere(x1):
        x1 = transform(x1)

#     if hasattr(x, 'warning'):
#         setattr(x1, 'warning', getattr(x, 'warning'))
#     
    return x1


def add_where_to_empty_list(result_of_function_above):
    r = result_of_function_above
    check_isinstance(r, CDP.ModelStatements)
    ops = unwrap_list(r.statements)
    if len(ops) == 0:
        l = make_list(ops, where=r.where)
        res = CDP.ModelStatements(l, where=r.where)
        return res
    else:
        return r

@parse_action
@wheredecorator
def mult_parse_action(tokens):
    tokens = list(tokens[0])
    l = make_list(tokens)
    assert l.where.character_end is not None
    res = CDP.MultN(l, where=l.where)
    return res

@parse_action
@wheredecorator
def divide_parse_action(tokens):
    tokens = list(tokens[0])
    l = make_list(tokens)
    assert l.where.character_end is not None
    res = CDP.Divide(l, where=l.where)
    return res

@parse_action
@wheredecorator
def plus_parse_action(tokens):
    tokens = list(tokens[0])
    l = make_list(tokens)
    assert l.where.character_end is not None
    res = CDP.PlusN(l, where=l.where)
    return res

@parse_action
@wheredecorator
def rvalue_minus_parse_action(tokens):
    tokens = list(tokens[0])
    l = make_list(tokens)
    assert l.where.character_end is not None
    res = CDP.RValueMinusN(l, where=l.where)
    return res

@parse_action
@wheredecorator
def fvalue_minus_parse_action(tokens):
    tokens = list(tokens[0])
    l = make_list(tokens)
    assert l.where.character_end is not None
    res = CDP.FValueMinusN(l, where=l.where)
    return res

    
@parse_action
def space_product_parse_action(tokens):
    tokens = list(tokens[0])
    ops = make_list(tokens)
    return CDP.SpaceProduct(ops, where=ops.where)

@parse_action
def mult_inv_parse_action(tokens):
    tokens = list(tokens[0])
    ops = make_list(tokens)
    return CDP.InvMult(ops, where=ops.where)

@parse_action
def plus_inv_parse_action(tokens):
    tokens = list(tokens[0])
    ops = make_list(tokens)
    return CDP.InvPlus(ops, where=ops.where)

def parse_wrap_filename(expr, filename):
    with open(filename) as f:
        contents = f.read()
    try:
        return parse_wrap(expr, contents)
    except MCDPExceptionWithWhere  as e:
        raise e.with_filename(filename)

def parse_wrap(expr, string):
    if isinstance(string, unicode):
        msg = 'The string is unicode. It should be a str with utf-8 encoding.'
        msg += '\n' + string.encode('utf-8').__repr__()
        raise ValueError(msg)
    
    check_isinstance(string, str)

    # Nice trick: the removE_comments doesn't change the number of lines
    # it only truncates them...
    string0 = remove_comments(string)

    m = lambda x: x
    try:
        from mcdp_lang_tests.utils import find_parsing_element
        from mcdp_library_tests.tests import timeit
        try:
            w = str(find_parsing_element(expr))
        except ValueError:
            w = '(unknown)'
        with timeit(w, 0.5):
            return expr.parseString(string0, parseAll=True)  # [0]
    except RuntimeError as e:
        msg = 'We have a recursive grammar.'
        msg += "\n\n" + indent(m(string), '  ') + '\n'
        raise_desc(DPInternalError, msg)
    except (ParseException, ParseFatalException) as e:
        where = Where(string0, character=e.loc) # note: string0
        e2 = DPSyntaxError(str(e), where=where)
        raise DPSyntaxError, e2, sys.exc_info()[2]
    except DPSemanticError as e:
        raise
#         msg = "User error while interpreting the model:"
#         msg += "\n\n" + indent(m(string), '  ') + '\n'
#         raise_wrapped(DPSemanticError, e, msg, compact=True)
    except DPInternalError as e:
        msg = "Internal error while evaluating the spec:"
        msg += "\n\n" + indent(m(string), '  ') + '\n'
        raise_wrapped(DPInternalError, e, msg, compact=False)

def remove_comments(s):
    lines = s.split("\n")
    def remove_comment(line):
        if '#' in line:
            return line[:line.index('#')]
        else:
            return line
    return "\n".join(map(remove_comment, lines))

def parse_line(line):
    from mcdp_lang.syntax import Syntax
    return parse_wrap(Syntax.line_expr, line)[0]

@contract(name= CDP.DPName)
def funshortcut1m(provides, fnames, prep_using, name):
    return CDP.FunShortcut1m(provides=provides,
                             fnames=fnames,
                             prep_using=prep_using,
                             name=name)
@contract(name=CDP.DPName)
def resshortcut1m(requires, rnames, prep_for, name):
    return CDP.ResShortcut1m(requires=requires, rnames=rnames, 
                             prep_for=prep_for, name=name)

def parse_pint_unit(tokens):
    tokens = list(tokens)
    pint_string = " ".join(tokens)
    return CDP.RcompUnit(pint_string)

