from .utils2 import eval_rvalue_as_constant_same
from comptests.registrar import comptest
from mcdp_lang.eval_resources_imp import eval_rvalue
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parse_interface import parse_ndp
from mcdp_lang.syntax import Syntax
from mocdp.comp.context import Context
from mocdp.exceptions import DPSemanticError

same = eval_rvalue_as_constant_same

@comptest
def check_tuples1():

    same("1 g + 1 kg", "1001 g")

@comptest
def check_tuples2():
    
    #s =     "take(<1g, 5J>, 1)"

    s = "<1g, 5J>"
    parsed = parse_wrap(Syntax.rvalue, s)[0]
    context = Context()
    ret = eval_rvalue(parsed, context)
    print ret

    same("take(<1g, 5J>, 1)", "5 J")

@comptest
def check_tuples3():
    res = parse_ndp("""
    mcdp {
        requires r [ J x g]
        
        r >= < 1J, 0g >
    }
    """)
    print res


@comptest
def check_tuples4():
    eval_rvalue_as_constant_same("max(1 g, 0 g)", "1g")
    eval_rvalue_as_constant_same("1 g + 1 kg", "1001 g")
    eval_rvalue_as_constant_same("max(1 g, 0 kg)", "1g")

@comptest
def check_tuples5():
    eval_rvalue_as_constant_same("take(<0 g, 10 g, 20g>, 1)", "10 g")

@comptest
def check_tuples6():
    parsef = lambda s: parse_wrap(Syntax.fvalue, s)[0]

    parsef('take(out, 1)')

    parse_wrap(Syntax.lf_tuple_indexing, 'take(required out, 1)')

    parsef('take(required out, 1)')

@comptest
def check_tuples7():

    res = parse_ndp("""
    mcdp {
        requires r [ product(a:J, b:g) ]
        
        take(required r, a) >= 1 J
        take(required r, b) >= 1 g
    }
    """)
    print res

    res = parse_ndp("""
    mcdp {
        requires r [ product(a:J, b:g) ]
        
        (required r).a >= 1 J
        (required r).b >= 1 g
    }
    """)
    print res

@comptest
def check_tuples8():
    res = parse_ndp("""
    mcdp {
        provides f [ product(a:J, b:g) ]
        
        take(provided f, a) <= 1 J
        take(provided f, b) <= 1 g
    }
    """)
    print res

    res = parse_ndp("""
    mcdp {
        provides f [ product(a:J, b:g) ]
        
        (provided f).a <= 1 J
        (provided f).b <= 1 g
    }
    """)
    print res
    
@comptest
def check_tuples9():
    """ unknown name """
    try:
        parse_ndp("""
        mcdp {
            requires r [ product(a:J, b:g) ]
            
            take(required r, x) >= 1 J
        }
        """)
    except DPSemanticError as e:
        print e
