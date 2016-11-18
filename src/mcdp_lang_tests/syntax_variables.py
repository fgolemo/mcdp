from comptests.registrar import comptest
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax
from mcdp_lang.parse_interface import parse_ndp
from mcdp_lang_tests.utils import assert_parse_ndp_semantic_error,\
    assert_parsable_to_unconnected_ndp, assert_parsable_to_connected_ndp

@comptest
def check_variables01():
    some = [
        'variable x [m]',
        'variable x [Nat]',
        'variable x [dimensionless]',
    ]
    expr = Syntax.var_statement
    for s in some:
        parse_wrap(expr, s)

@comptest
def check_variables02():
    s = """
    mcdp {
        provides f [Nat]
        requires r [Nat]
        
        variable x [Nat]

        provided f <= x
        x <= required r
    }
    """        
    parse_ndp(s)


@comptest
def check_variables03():
    # This causes an error because the variable x is not used.
    # In the future there should be a warning or more explicit error.
    s = """
    mcdp {
        provides f [Nat]
        requires r [Nat]
        
        variable x [Nat] # declared but not used

        provided f <= required r
    }
    """
    assert_parsable_to_unconnected_ndp(s)
    


@comptest
def check_variables04():
    # This causes an error because it conflicts with f
    s = """
    mcdp {
        provides f [Nat]
        requires r [Nat]
        
        variable f [Nat]

    }
    """
    assert_parse_ndp_semantic_error(s, 'Conflict')

@comptest
def check_variables05():
    # This causes an error because it conflicts with r
    s = """
    mcdp {
        provides f [Nat]
        requires r [Nat]
        
        variable r [Nat]
    }
    """
    assert_parse_ndp_semantic_error(s, 'Conflict')


@comptest
def check_variables06():
    # This causes an error because it is repeated
    s = """
    mcdp {
        provides f [Nat]
        requires r [Nat]
        
        variable x [Nat]
        variable x [Nat]
    }
    """
    expect = "Variable name 'x' already used once"
    print assert_parse_ndp_semantic_error(s, expect)

@comptest
def check_variables07():
    # This causes an error because it conflicts with a 
    # name used for resource
    s = """
    mcdp {
        provides f [Nat]
        requires r [Nat]
        
        x = provided f
        variable x [Nat]
    }
    """
    print assert_parse_ndp_semantic_error(s, 'already used as a resource')


@comptest
def check_variables08():
    # This causes an error because it conflicts with a 
    # name used for functionality
    s = """
    mcdp {
        provides f [Nat]
        requires r [Nat]
        
        x = required r
        variable x [Nat]
    }
    """
    print assert_parse_ndp_semantic_error(s, 'already used as a functionality')


@comptest
def check_variables09():
    """ This is not connected. """
    s = """
    mcdp {
        provides f [Nat]
        requires r [Nat]
        
        variable x [Nat]
        
        x >= provided f 
    }
    """
    assert_parsable_to_unconnected_ndp(s)

@comptest
def check_variables10():
    """ This is not connected. """
    s = """
    mcdp {
        provides f [Nat]
        requires r [Nat]
        
        variable x [Nat]
        
        x <= required r 
    }
    """
    assert_parsable_to_unconnected_ndp(s)
    
@comptest
def check_variables11():
    s = """
mcdp {
    provides z [Nat]

    variable x [Nat]
    variable y [Nat]

    x + y >= ceil(sqrt(x)) + ceil(sqrt(y)) + provided z

    requires x, y
}
    """
    ndp = parse_ndp(s)
    dp = ndp.get_dp()
    for i in range(6):
        res = dp.solve(i)
        print('%2d: %s' % (i, res))
    

@comptest
def check_variables12():
    s = """
mcdp {
    provides z [Nat]

    variable x, y [Nat]

    x + y >= ceil(sqrt(x)) + ceil(sqrt(y)) + provided z

    requires x, y
}
    """
    parse_ndp(s)


@comptest
def check_variables13(): # TODO: rename  check_resources_shortcut4a()
    s = """
mcdp {
    provides z [Nat]

    variable x, y [Nat]

    x + y >= ceil(sqrt(x)) + ceil(sqrt(y)) + provided z

    requires x, y
}
    """
    assert_parsable_to_connected_ndp(s)
    
    s = """
mcdp {
    provides z [Nat]

    requires z
}
    """
    assert_parsable_to_connected_ndp(s)
    
    
    
@comptest
def check_variables14():
    s = """
mcdp {
    provides z [Nat]

    variable x, y [Nat]

    x + y >= ceil(sqrt(x)) + ceil(sqrt(y)) + provided z

    requires x, notfound
}
    """
    expect = "Could not find required resource expression 'notfound'"
    print assert_parse_ndp_semantic_error(s, expect)
    
    s = """
mcdp {
    variable x [Nat]

    x >= Nat: 0
     
    requires x [Nat] 
}
    """
    expect = "The name 'x' is already used by a variable"
    print assert_parse_ndp_semantic_error(s, expect)

    s = """
mcdp {
    variable x [Nat]

    x <= Nat: 0
     
    provides x [Nat] 
}
    """
    expect = "The name 'x' is already used by a variable"
    print assert_parse_ndp_semantic_error(s, expect)

@comptest
def check_variables15():
    s = """
mcdp {
    variable x, y [Nat]
    variable z [Nat]
    
    x + y >= ceil(sqrt(x)) + ceil(sqrt(y)) + z

    requires x, y
    provides z
}
    """
    
    assert_parsable_to_connected_ndp(s)
    s = """
mcdp {
    requires z [Nat]

    provides z
}
    """
    assert_parsable_to_connected_ndp(s)

    s = """
mcdp {
    requires z [Nat]
    requires y [Nat]

    provides z, y
}
    """
    assert_parsable_to_connected_ndp(s)
