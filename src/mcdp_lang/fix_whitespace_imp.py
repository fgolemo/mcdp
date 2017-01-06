from mcdp_lang.refinement import namedtuple_visitor_ext
from mcdp_lang.namedtuple_tricks import get_copy_with_where
from contracts.interface import Where


def fix_whitespace(root):
    def transform(x, parents):  # @UnusedVariable
        if x is root:
            return x
        w = x.where
        ws = w.string[w.character:w.character_end]
        if ws.strip() != ws:
            is_whitespace = lambda x : x in  [' ', '\n']
            i = 0
            while is_whitespace(ws[i]) and i < len(ws) - 1:
                i += 1
            ninitial = i
            
            j = len(ws) -1
            while is_whitespace(ws[j]) and j > 0:
                j -= 1
                
            ntrailing = (len(ws) - 1) - j
            
            character = w.character + ninitial
            character_end = w.character_end - ntrailing
            where2 = Where(w.string, character, character_end)
                
            x2 = get_copy_with_where(x, where2)

            return x2
        else:
            return x
        
    return namedtuple_visitor_ext(root, transform)