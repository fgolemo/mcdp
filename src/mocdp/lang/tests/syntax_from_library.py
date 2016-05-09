from comptests.registrar import comptest
from mocdp.lang.parse_actions import parse_wrap
from mocdp.lang.syntax import Syntax

@comptest
def check_from_library1():

    res = parse_wrap(Syntax.dpinstance_expr, 'instance load S')[0]
    res = parse_wrap(Syntax.dpinstance_expr, 'instance load(S)')[0]
    res = parse_wrap(Syntax.dpinstance_expr, 'instance load "S"')[0]
    res = parse_wrap(Syntax.dpinstance_expr, 'instance load("S")')[0]
    res = parse_wrap(Syntax.dpinstance_expr, "instance load 'S'")[0]
    res = parse_wrap(Syntax.dpinstance_expr, "instance load('S')")[0]

    res = parse_wrap(Syntax.dpinstance_expr, "from_library ('S')")[0]
    res = parse_wrap(Syntax.dpinstance_expr, "from_library('S')")[0]
    res = parse_wrap(Syntax.dpinstance_expr, "from_library 'S' ")[0]
    res = parse_wrap(Syntax.dpinstance_expr, "from_library S ")[0]
    res = parse_wrap(Syntax.dpinstance_expr, "new S")[0]

    print res
#
#     x = from_library "S"
#
#     x = from_library 'S'
#
#     parse_wrap(Syntax.rvalue, 'mission_time')



