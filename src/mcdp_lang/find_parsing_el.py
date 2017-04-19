from contracts import contract


class ParsingElement(object):
    def __init__(self, name):
        self.name = name
    def get(self):
        from .syntax import Syntax
        return getattr(Syntax, self.name) # bug
    def __repr__(self):
        return 'ParsingElement(%s)' % self.name


@contract(returns=ParsingElement)
def find_parsing_element(x):
    from .syntax_codespec import SyntaxCodeSpec
    from .syntax import Syntax, SyntaxBasics

    d = dict(**Syntax.__dict__)    # @UndefinedVariable
    d.update(**SyntaxCodeSpec.__dict__)  # @UndefinedVariable
    d.update(**SyntaxBasics.__dict__)  # @UndefinedVariable

    for name, value in d.items():  # @UndefinedVariable
        if value is x:
            return ParsingElement(name)

    raise ValueError('Cannot find element for %s.' % str(x))
