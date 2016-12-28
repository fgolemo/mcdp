# -*- coding: utf-8 -*-
from collections import namedtuple, defaultdict
from mocdp.memoize_simple_imp import memoize_simple


def replace_inside_equations(s):
    """ Processing inside equations """
    
    rs = get_replacements()
#     counts = defaultdict(lambda: 0)
    for _ in rs:
        s = s.replace(_.text, _.latex) 
    return s
    
replacement = namedtuple('replacement', 'text latex')

@memoize_simple
def get_replacements():
    """ Returns a list of replacement objects """
    x = [
        ('⟶', '\\rightarrow'),
        ('⟼', '\\mapsto'),
        ('⟨', '\\langle'),
        ('⟩', '\\rangle'),
        ('≤', '\\leq'),
        ('≥', '\\geq'),
        ('₁', '_{1}'),
        ('₂', '_{2}'),
        ('ₐ', '_{a}'),
        ('ₐ', '_{a}'),
        ('₂', '_{b}'),
        ('ₙ', '_{n}'),
        ('₊', '_{+}'),
        ('ℝ', '\\mathbb{R}'),
        ('ℕ', '\\mathbb{N}'),
        ('×', '\\times'),
        ('∞', '\\infty'),
        ('∈', '\\in'),
        ('⟦', '\\llbracket'),
        ('⟧', '\\rrbracket'),
        ('≐', '\\doteq'),
        ('⊆', '\\subseteq'),
        ('⊇', '\\supseteq'),
        ('±','\\pm'),
        ('…','\\dots'),
        ('↑','\\uparrow'),
        ('↓','\\downarrow'),
        ('∩','\\cap'),
        ('○','\\circ'),
        ('∪','\\bigcup'),
        ('≼','\\posleq'),
        ('≺','\\poslt'),
        ('≽','\\posgeq'),
        ('≻','\\posgt'),
        ('⊤','\\top'),
        ('⊥','\\bot'),
        ('≡','\\equiv'),
        ('⌑','\\,'), # arbitrary
        ('␣','\\ '), # arbitrary
        ('⍽','\\quad'), # arbitrary
    ]
    
    from mcdp_lang.dealing_with_special_letters import greek_letters
    for letter_name, symbol in greek_letters.items():
        symbol = symbol.encode('utf-8')
        letter_name = str(letter_name)
        x.append((symbol, '\\' + letter_name))
    
    res = [replacement(text=a, latex=b) for a, b in x]
    return res

def count_possible_replacements(fn):
    from .latex_preprocess import extract_maths
    
    s = open(fn).read()
    rs = get_replacements()
    latex2text = dict((_.latex, _.text) for _ in rs)
    
    for _ in rs:
        print('%s     %s' % (_.text, _.latex))
    
    s, subs = extract_maths(s)
    
    counts = defaultdict(lambda : 0)
    for r in rs:
        lookfor = r.latex
        for _, v in subs.items():
            n = v.count(lookfor)
            if n > 0:
                counts[lookfor] += n 
    
    counted = sorted(counts, key=lambda k: -counts[k])
    print('counters:')
    for c in counted:
        print('   %3d   %14s  %s' % (counts[c], c, latex2text[c])) 
    
    



