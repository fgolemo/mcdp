# -*- coding: utf-8 -*-

"""
    
    For syntax, use assert_syntax_error or parse_wrap_check:

    ```
    assert_syntax_error('1', Syntax.floatnumber)
    parse_wrap_check('1', Syntax.integer_or_float)
    parse_wrap_check('1', Syntax.integer_or_float, CDP.ValueExpr(1))
    ```
    
    These two make sure that you can parse and NDP, and if it is connected or not:
    
    assert_parsable_to_connected_ndp
    assert_parsable_to_unconnected_ndp
    assert_parse_ndp_semantic_error(string, contains)
    
    Also useful:
        
        eval_rvalue_as_constant
        
        eval_rvalue_as_constant_same
        
        eval_rvalue_as_constant_same_exactly
        
        parse_wrap_semantic_error
        
        
"""

from .examples import *
from .failures_parsing import *
from .failures_simplification import *
from mcdp_lang_tests.syntax_math import *
from .syntax_anyof import *
from .syntax_approximation import *
from .syntax_asserts import *
from .syntax_canonical import *
from .syntax_catalogue import *
from .syntax_connections import *
from .syntax_conversions import *
from .syntax_coproduct import *
from .syntax_from_library import *
from .syntax_import import *
from .syntax_intervals import *
from .syntax_load import *
from .syntax_minimals_maximals import *
from .syntax_minmax import *
from .syntax_misc import *
from .syntax_multiset import *
from .syntax_named_tuples import *
from .syntax_numbers import *
from .syntax_power import *
from .syntax_sets import *
from .syntax_single_space import *
from .syntax_spaces  import *
from .syntax_tuples  import *
from .syntax_uncertainty import *
from .take_optimization import *
from .templates_test import *
from .syntax_variables import *
from .syntax_derivative import *

from .syntax_comments import *
from .parsing_error_recovery import *

from .misc_corner_cases import *

from .todo import *

from .test_suggestion import *