# -*- coding: utf-8 -*-
from contracts.utils import indent

def indent_plus_invisibles(x, c='  |'):
    return indent(make_chars_visible(x),c)
    
def make_chars_visible(x):
    """ Replaces whitespaces ' ' and '\t' with '␣' and '⇥' """
    from mcdp.constants import MCDPConstants
    x = x.replace(' ', '␣')
    if MCDPConstants.tabsize == 4:
        tab = '├──┤'
    else:
        tab = '⇥'
    x = x.replace('\t', tab)
#     nl = '␤\n'
    nl = '⏎\n'
    x = x.replace('\n', nl)
    return x

