# -*- coding: utf-8 -*-
from comptests.registrar import comptest, run_module_tests
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax

from .utils import assert_parsable_to_connected_ndp


@comptest
def check_catalogue1():
    s = """
     a_ | 50 g | `scientific_objectives : find_ancient_life
    """
    parse_wrap(Syntax.catalogue_row, s)[0]
    
@comptest
def check_catalogue2():

    s = """

catalogue {
     provides plutonium [g]
     requires science [`scientific_objectives]    
     a_ | 50 g | `scientific_objectives : find_ancient_life
}
    
    """
    parse_wrap(Syntax.ndpt_catalogue_dp, s)[0]
   
    
@comptest
def check_catalogue_implicity():

    s = """
catalogue {
    provides f1 [m]    
    requires r1 [g]
    10 m ⟷ 1 g
    10 m <-> 1 g
}
    """
    assert_parsable_to_connected_ndp(s)
     
    
@comptest
def check_catalogue_implicity2():

    s = """
catalogue {
    provides f1 [m]    
    provides r1 [g]
}
    """
    assert_parsable_to_connected_ndp(s)
#     dp = ndp.get_dp()
#     I = dp.get_imp_space()
    
@comptest
def check_catalogue_no_funcs():
    """ multi functionality """
    s = """
catalogue {
    requires r1 [m]    
    <> ⟻ a ⟼ 10 m
}
    """
    assert_parsable_to_connected_ndp(s)

@comptest
def check_catalogue_no_res():
    """ multi functionality """
    s = """
catalogue {
    provides f1 [m]    
    10 m ⟻ a ⟼ <>  
}
    """
    assert_parsable_to_connected_ndp(s)
    
@comptest
def check_catalogue_multi_res():
    """ multi functionality """
    s = """
catalogue {
    provides f1 [g]
    requires r1 [m]    
    requires r2 [g]
    2 mg ⟻ a ⟼ 10 m, 1g
}
    """
    assert_parsable_to_connected_ndp(s)
    

@comptest
def check_catalogue_multi_fun():
    """ multi functionality """
    s = """
catalogue {
    provides f1 [g]
    provides f2 [m]
    requires r [m]    
    1 g, 2 m ⟻ a ⟼ 10 m 
}
    """
    assert_parsable_to_connected_ndp(s)




@comptest
def check_catalogue6():
    
    s = """
catalogue {
    provides f [g]
    requires r [m]    
     
    10 g <-| a |-> 10 m
    10 g <-| b |-> 10 m
}
    """
    parse_wrap(Syntax.ndpt_catalogue2, s)
    parse_wrap(Syntax.ndpt_dp_rvalue, s)
    
       
    s = """
catalogue {
    provides f [g]
    requires r [m]    
    10 g ⟻ a ⟼ 10 m
    10 g ⟻ b ⟼ 10 m
}
    """
    parse_wrap(Syntax.ndpt_catalogue2, s)
    parse_wrap(Syntax.ndpt_dp_rvalue, s)

    s = """
catalogue {
    provides f [g]
    requires r [m]    
    10 g ↤ a ↦ 10 m
    10 g ↤ b ↦ 10 m
}
    """
    
    parse_wrap(Syntax.ndpt_catalogue2, s)[0]
    parse_wrap(Syntax.ndpt_dp_rvalue, s)


@comptest
def check_catalogue5(): 
    parse_wrap(Syntax.MAPSFROM, '<-|' )
    parse_wrap(Syntax.MAPSFROM, '<--|' )
    parse_wrap(Syntax.MAPSFROM, '<---|' )
    parse_wrap(Syntax.MAPSFROM, '<----|' )
    parse_wrap(Syntax.MAPSFROM, '⟻' )
    parse_wrap(Syntax.MAPSFROM, '↤' )
    parse_wrap(Syntax.MAPSTO, '|->' )
    parse_wrap(Syntax.MAPSTO, '|-->' )
    parse_wrap(Syntax.MAPSTO, '|--->' )
    parse_wrap(Syntax.MAPSTO, '|---->' )
    parse_wrap(Syntax.MAPSTO, '⟼' )
    parse_wrap(Syntax.MAPSTO, '↦' )
    parse_wrap(Syntax.LEFTRIGHTARROW, '⟷' )
    parse_wrap(Syntax.LEFTRIGHTARROW, '<->' )
    parse_wrap(Syntax.LEFTRIGHTARROW, '<-->' )
    parse_wrap(Syntax.LEFTRIGHTARROW, '<--->' )
    parse_wrap(Syntax.LEFTRIGHTARROW, '<---->' )

    parse_wrap(Syntax.catalogue_func, '1 g')
    parse_wrap(Syntax.catalogue_func, '1, 2 g')
    parse_wrap(Syntax.catalogue_res, '1 g')
    parse_wrap(Syntax.catalogue_res, '1, 2 g')
    parse_wrap(Syntax.catalogue_row2, '1, 2 g <--| a |-> 1 m')
    parse_wrap(Syntax.catalogue_row2, '1 <-| a |-> 2')
    parse_wrap(Syntax.catalogue_row2, '1 ⟻ a ⟼ 2')
    
if __name__ == '__main__': 
    
    run_module_tests()
    