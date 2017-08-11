# -*- coding: utf-8 -*-
from collections import OrderedDict
import string


def render_number(n, style):
    if not style in number_styles:
        msg = 'Invalid style %r not in %s' % (style, sorted(number_styles))
        raise ValueError(msg)
    seq = number_styles[style]
    ns = len(seq)
    assert ns > 20, (style, seq)
    if n >= (ns-1)**2:
        raise NotImplementedError('%s > %s' % (n, (ns-1)**2))
    elif n + 1>= 2*ns:
        q, r = divmod(n+2, ns)
        return seq[q] + "-" + seq[r] #+ '-x2'
    elif n >= ns:
        q, r = divmod(n+1, ns)
        return seq[q] + "-" + seq[r] #+ '-x1'
    else:
        return seq[n]


def write_roman(num):
    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, _ = divmod(num, r)
            yield roman[r] * x
            num -= (r * x)
            if num > 0:
                roman_num(num)
            else:
                break

    return "".join([a for a in roman_num(num)])
    
    
ZERO = 'zero-counter'

number_styles = {
    'lower-alpha': [ZERO,] + list(string.ascii_lowercase),
    'upper-alpha': [ZERO,] + list(string.ascii_uppercase),
    'lower-latin': [ZERO,] + list(string.ascii_lowercase), 
    'upper-latin': [ZERO,] + list(string.ascii_uppercase),
    'decimal': map(str, range(0, 500)),
    'lower-greek': map(str, range(0, 26)), # todo
    'upper-greek': map(str, range(0, 26)), # todo
    'lower-roman': [ZERO,]+[write_roman(_).lower() for _ in range(1, 100)], 
    'upper-roman': [ZERO,]+[write_roman(_).upper() for _ in range(1, 100)],
} 
 

