# operators
from collections import namedtuple

Mult = namedtuple('Mult', 'a b')
Resource = namedtuple('Resource', 'dp s')
NewFunction = namedtuple('NewFunction', 'name')
Constraint = namedtuple('Constraint', 'dp2 s2 rvalue')

LoadCommand = namedtuple('LoadCommand', 'load_arg')
SetName = namedtuple('SetName', 'name dp_rvalue')
