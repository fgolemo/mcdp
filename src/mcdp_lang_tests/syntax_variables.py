from comptests.registrar import comptest

@comptest
def check_variables01():
    pass
    def x():
        idn = SyntaxIdentifiers.get_idn()
        parse_wrap(idn, 'battery')
        parse_wrap(idn, 'battery ')
        expr = idn + Literal('=')
        parse_wrap(expr, 'battery=')
        parse_wrap(Syntax.ndpt_load, 'load battery')
    
    @comptest
    def check_lang3_times():
        parse_wrap(Syntax.rvalue, 'mission_time')
    
    
    @comptest
    def check_lang4_composition():
        parse_wrap(Syntax.rvalue, 'mission_time')
    
        s = """
    dp {
        provides current [A]
        provides capacity [J]
        requires weight [g]
        
        implemented-by load times
    }
        """
        parse_wrap(Syntax.ndpt_simple_dp_model, s)[0]

@comptest
def check_variables02():
    pass

@comptest
def check_variables03():
    pass

@comptest
def check_variables04():
    pass

@comptest
def check_variables05():
    pass

@comptest
def check_variables06():
    pass

@comptest
def check_variables07():
    pass

@comptest
def check_variables08():
    pass

@comptest
def check_variables09():
    pass

@comptest
def check_variables10():
    pass

@comptest
def check_variables11():
    pass

@comptest
def check_variables12():
    pass

@comptest
def check_variables13():
    pass

@comptest
def check_variables14():
    pass

@comptest
def check_variables15():
    pass

