from comptests.registrar import comptest
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax

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
def check_catalogue3():
    pass


@comptest
def check_catalogue4():
    pass


@comptest
def check_catalogue5():
    pass

@comptest
def check_catalogue6():
    pass

