from contracts.utils import raise_desc
from multi_index import get_it

A = ['a', ['b', 'c']]
   
   
cases = [
  (A, (), ['a', ['b', 'c']]),
  (A, 0, 'a'),
  (A, 1, ['b', 'c']),
  (A, [0, 0], ['a', 'a']),
  (A, [(), ()], [['a', ['b', 'c']], ['a', ['b', 'c']]]),
  (A, [0, (1, 1)], ['a', 'c']),
]     

def test_cases():

    for X, index, result in cases:
        yield check_case, X, index, result

def check_case(X, index, expected):

    res = get_it(X, index, reduce_list=list)
    if res != expected:
        msg = 'Result is different.'
        raise_desc(ValueError, msg, X=X, index=index, expected=expected, res=res)
    
