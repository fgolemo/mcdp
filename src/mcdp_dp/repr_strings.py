# -*- coding: utf-8 -*-
from mcdp_maps.repr_map import get_string_vector, get_string_list_of_elements


def repr_h_map_parallel(letter, n, mapname):
    elements = get_string_list_of_elements(letter, n)
    start = get_string_vector(letter, n)
    res = ' × '.join('%s%s(%s)' % (mapname, i+1, e) for i, e in zip(range(n), elements))
    return '%s ⟼ %s' % (start, res) 


def repr_hd_map_meetndp(letter, n, top='⊤'):
    """ r ⟼ { ⟨r,⊤,⊤⟩, ⟨⊤,r,⊤⟩, ⟨⊤,⊤,r⟩ } """
    def element_i(i):
        tops = [top] * n
        tops[i] = letter
        res = "⟨%s⟩" % (",".join(tops))
        return res
    elements = map(element_i, range(n))
    elements = ", ".join(elements)
    return "%s ⟼ { %s }" % (letter, elements)

# TODO: change name

def invplus2_repr_h_map(x, y):
    # s = "x ⟼ {⟨y1, y2⟩ | y1 + y2 = x}"
    return inv_repr_h_map(x, y, 2, '', '=', '+')


def invplus2_repr_hd_map(x):
    s = "⟨x1, x2⟩ ⟼ x1 + x2"
    return s.replace('x', x) 


def repr_hd_map_sumn(n, U_or_L=None, napprox=None):
    s = inv_repr_h_map('r', 'f', n, '', '=', '+')
    if U_or_L is not None:
        s =  s.replace('⟼ ', '⟼ app%s(%s,') % (U_or_L, napprox) + ')'
    return s
    
    
def repr_h_map_invmult(n, 
#                        U_or_L=None, napprox=None
                       ):
    s = inv_repr_h_map('r', 'f', n, 'Min', '≤', "⋅")
#     if U_or_L is not None:
#         s =  s.replace('⟼ ', '⟼ app%s(%s,') % (U_or_L, napprox) + ')'
    return s


def repr_hd_map_productn(n, U_or_L=None, napprox=None):
    s = inv_repr_h_map('r', 'f', n, 'Max', '≤', "⋅")
    if U_or_L is not None:
        s =  s.replace('⟼ ', '⟼ app%s(%s,') % (U_or_L, napprox) + ')'
    return s 


def inv_repr_h_map(x, y, ny, op, comp, opera):
    v1 = get_string_vector(y, ny)
    m = opera.join(get_string_list_of_elements(y, ny))
    s = "%s ⟼ %s {%s | %s %s %s}" % (x, op, v1, m, comp, x)
    return s
