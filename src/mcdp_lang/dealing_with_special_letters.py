# -*- coding: utf-8 -*-
from contracts.utils import check_isinstance
from contracts import contract

greek_letters = {
    u'alpha': u'α',
    u'beta': u'β',
    u'gamma': u'γ',
    u'delta': u'δ',
    u'epsilon': u'ε',
    u'zeta': u'ζ',
    u'eta':u'η',
    u'theta':u'θ',
    u'iota':u'ι',
    u'kappa':u'κ',
    u'lambda':u'λ',
    u'mu':u'μ',
    u'nu':u'ν',
    u'xi':u'ξ',
    u'omicron':u'ο',
    u'pi':u'π',
    u'rho': u'ρ',
    u'sigma':u'σ', # 'ς',
    u'tau':u'τ', 
    u'upsilon':u'υ',
    u'phi':u'φ',
    u'chi':u'χ',
    u'psi':u'ψ',
    u'omega':u'ω',   
    u'Gamma':u'Γ',
    u'Chi':u'Χ',
    u'Delta':u'Δ',
    u'Epsilon':u'Ε',
    u'Zeta':u'Ζ',
    u'Eta':u'Η',  
    u'Theta':u'Θ',
    u'Iota':u'Ι',
    u'Kappa':u'Κ',
    u'Lambda':u'Λ',
    u'Mu':u'Μ',
    u'Nu':u'Ν',     
    u'Xi':u'Ξ',
    u'Omicron':u'Ο',
    u'Pi':u'Π',
    u'Rho':u'Ρ',
    u'Sigma':u'Σ',
    u'Tau': u'Τ',
    u'Upsilon': u'Υ',
    u'Phi': u'Φ',
    u'Chi': u'Χ',
    u'Psi': u'Ψ',
    u'Omega': u'Ω',
}
greek_letters_utf8 = dict( (k.encode('utf8'),v.encode('utf8')) for k,v in greek_letters.items())

subscripts = { 
    0: u'₀',
    1: u'₁',
    2: u'₂',
    3: u'₃',
    4: u'₄',
    5: u'₅',
    6: u'₆',
    7: u'₇',
    8: u'₈',
    9: u'₉',
}

subscripts_utf8 = dict( (k, v.encode('utf8')) for k, v in subscripts.items())

# these count as dividers
dividers = ['_','0','1','2','3','4','5','6','7','8','9']
dividers.extend(sorted(subscripts_utf8.values()))

@contract(s=bytes)
def ends_with_divider(s):
    check_isinstance(s, bytes)
    if not s: return False
    last_char = unicode(s, 'utf-8')[-1].encode('utf8')
    #print('last_char: %s %r' % (last_char, last_char))
    return  last_char in dividers

@contract(s=bytes)
def starts_with_divider(s):
    check_isinstance(s, bytes)
    if not s: return False
    first_char = unicode(s, 'utf-8')[0].encode('utf8')
    #print('last_char: %s %r' % (first_char, first_char))
    return first_char in dividers

