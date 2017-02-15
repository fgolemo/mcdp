# -*- coding: utf-8 -*-
from collections import namedtuple, defaultdict
from mcdp.utils.memoize_simple_imp import memoize_simple


def replace_inside_equations(s):
    """ Processing inside equations """
    
    rs = get_replacements()
#     counts = defaultdict(lambda: 0)
    for _ in rs:
        latex = _.latex
        if latex.startswith('\\'):
            latex = latex + ' '
        s = s.replace(_.text, latex) 
    return s
    
replacement = namedtuple('replacement', 'text latex')

@memoize_simple
def get_replacements():
    """ Returns a list of replacement objects """
    x = [
        ('→', '\\rightarrow'),
        ('⇒','\\Rightarrow'),
        ('↦', '\\mapsto'),
        ('⟨', '\\langle'),
        ('⟩', '\\rangle'),
        ('≤', '\\leq'),
        ('≥', '\\geq'),
#         0: u'₀',
#     1: u'₁',
#     2: u'₂',
#     3: u'₃',
#     4: u'₄',
#     5: u'₅',
#     6: u'₆',
#     7: u'₇',
#     8: u'₈',
#     9: u'₉',
        ('₀', '_{0}'),
        ('₁', '_{1}'),
        ('₂', '_{2}'),
        ('ₐ', '_{a}'),
        ('ᵢ', '_{i}'),
        ('ⁱ', '^{i}'),
        ('ₒ', '_{o}'),
        ('ᵦ', '_{\beta}'),
#         ('₂', '_{b}'),
        ('ₙ', '_{n}'),
        ('ⱼ','_{j}'),
        ('₊', '_{+}'),
        ('ₜ', '_{t}'),
        ('∃','\exists'),
        ('∀','\forall'),
        ('ℝ', '\\mathbb{R}'),
        ('ℕ', '\\mathbb{N}'),
        ('ℚ', '\\mathbb{Q}'),
        
        ('×', '\\times'),
        ('∞', '\\infty'),
        ('∈', '\\in'), # only if followed by '\'
        ('⟦', '\\llbracket'),
        ('⟧', '\\rrbracket'),
        ('≐', '\\doteq'),
        ('⊂', '\\subset'),
        ('⊃', '\\supset'),
        ('⊆', '\\subseteq'),
        ('⊇', '\\supseteq'),
        ('±','\\pm'),
        ('…','\\dots'),
#         ('↑','\\uparrow'),
#         ('↓','\\downarrow'),
        ('∩','\\cap'),
        ('∪', '\\cup'),
        ('○','\\circ'),
        ('∪','\\bigcup'),
        ('∪','\\bigcup'),
        ('≼','\\posleq'),
        ('≺','\\poslt'),
        ('≽','\\posgeq'),
        ('≻','\\posgt'),
        ('⊤','\\top'),
        ('⊥','\\bot'),
        ('≡','\\equiv'),
        ('∧', '\\wedge'),
        ('∨', '\\vee'),
        ('⌑','\\,'), # arbitrary
        ('␣','\\ '), # arbitrary
        ('⍽','\\quad'), # arbitrary
        ('⎵', '\\quad'),
        ('∏','\\prod'),
        ('∫','\\int'),
        ('★', '\\star'),
        ('½', '\\frac{1}{2}'),
        
        ('𝒩', '\\mathcal{N}'),
        ('ℰ', '\\mathcal{E}'),
        
        ('ℱ', '\\funsp'),
        ('ℛ', '\\ressp'),
        ('𝒫', '\\posA'),
        ('𝒬', '\\posB'),
        ('↑','\\upit'),
        ('↓','\\downarrow'),
        ('⌈','\\lceil'),
        ('⌉','\\rceil'),
        
        ('∅','\\emptyset'),
        ('𝖿', '\\fun'),
        ('𝗋', '\\res'),
        ('𝗁', '\\ftor'),
        ('𝐖', '\\mathbf{W}'),
        ('𝐲', '\\boldsymbol{𝐲}'),
        ('𝖠', '\\antichains'),
        ('𝖴', '\\upsets'),
        ('𝖫', '\\lowersets'),
        ('𝗌𝗎𝗉', '\\sup'),
        ('𝗆𝗂𝗇', '\\min'),
        ('𝗅𝖿𝗉', '\\lfp'),
        ('⦃', '\\{'),
        ('⦄', '\\}'),
        ('𝖬𝗂𝗇', '\\𝖬in'),
        ('𝟏', '\\One'),
        # TODO:
        # \star
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
    
#     for _ in rs:
#         print('%s     %s' % (_.text, _.latex))
    
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
    
    



