# -*- coding: utf-8 -*-

def repr_map_invmultvalue(letter, c_space, c_value):
    c = c_space.format(c_value)
    return "%s ⟼ %s / (%s)" % (letter, letter, c)

def repr_map_multvalue(letter, space, value):
    c = ' %s' % space.format(value)
    return  '%s ⟼ %s × %s' % (letter, letter, c)

def repr_map_invmultdual(letter, value, space):
    return repr_map_multvalue(letter, value, space)
    
    
def repr_map_joinn(letter, n):
    elements = get_string_list_of_elements(letter, n)
    start = "⟨" +" , ".join(elements) + "⟩"
    transformed = " ∧ ".join(elements)
    return '%s ⟼ %s' % (start, transformed)

def repr_map_meetn(letter, n):
    elements = get_string_list_of_elements(letter, n)
    transformed = " ∨ ".join(elements)    
    start = get_string_vector(letter, n)
    return '%s ⟼ %s' % (start, transformed)

def get_string_vector(letter, n):
    """ Returns ⟨r₁, ..., rₙ⟩ """
    elements = get_string_list_of_elements(letter, n)
    start = "⟨" +", ".join(elements) + "⟩"
    return start

def get_string_list_of_elements(letter, n):
    """ Returns ["r1", "r2", ...] """
    def sub(i):
        # indices = list("₁₂₃₄₅₆₇₈₉")  # ₀
        indices = [str(_+1) for _ in range(n)]
        
        if i >= len(indices): return '%d' % i
        return indices[i]
    elements = [letter + sub(i) for i in range(n)]
    return elements

def repr_map_product(letter, n):
    start = get_string_vector(letter, n)
    elements = get_string_list_of_elements(letter, n)
    transformed =  "⋅".join(elements)
    return "%s ⟼ %s" % (start, transformed)

def plusvaluedualmap_repr(letter, space, value):
    c = space.format(value)
    return  '%s ⟼ %s - %s if %s ≽ %s, else ø' % (letter, letter, c, letter, c)
            
def plusvaluemap_repr(letter, space, value):
    label = '+ %s' % space.format(value)
    return  '%s ⟼ %s %s' % (letter, letter, label)

def minusvaluemap_repr(letter, space, value):
    label = '- %s' % space.format(value)
    return  '%s ⟼ %s %s' % (letter, letter, label)

def sumn_repr_map(letter, n):
    start = get_string_vector(letter, n)
    elements = get_string_list_of_elements(letter, n)
    transformed =  " + ".join(elements)
    return "%s ⟼ %s" % (start, transformed)