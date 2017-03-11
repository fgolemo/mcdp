# -*- coding: utf-8 -*-
from contracts.utils import raise_desc
from mcdp_lang_utils.where_utils import line_and_col, location

from .where_utils import printable_length_where
from mcdp_utils_misc.string_repr import make_chars_visible


class Where(object):
    """
        An object of this class represents a place in a file, or an interval.

        All parsed elements contain a reference to a :py:class:`Where` object
        so that we can output pretty error messages.
        
        
        Character should be >= len(string) (possibly outside the string).
        Character_end should be >= character (so that you can splice with 
        string[character:character_end])
    """

    def __init__(self, string, character, character_end=None):
        if not isinstance(string, str):
            raise ValueError('I expect the string to be a str, not %r' % string)
        
        if not (0 <= character <= len(string)):
            msg = ('Invalid character loc %s for string of len %s.' %
                    (character, len(string)))
            raise_desc(ValueError, msg, string=string.__repr__())
            # Advance pointer if whitespace
            # if False:
            #     while string[character] == ' ':
            #         if character_end is not None:
            #             assert character <= character_end
            #         if (character < (len(string) - 2)) and ((character_end is None)
            #                                             or (character <= character_end - 1)):
            #             character += 1
            #         else:
            #             break  
        self.line, self.col = line_and_col(character, string)

        if character_end is not None:
            if not (0 <= character_end <= len(string)):
                msg = ('Invalid character_end loc %s for string of len %s.'% 
                       (character_end, len(string)))
                
                raise_desc(ValueError, msg, string=string.__repr__())
        
            if not (character_end >= character):
                msg=  'Invalid interval [%d:%d]' % (character, character_end)
                raise ValueError(msg)

            self.line_end, self.col_end = line_and_col(character_end, string)
        else:
            self.line_end, self.col_end = None, None
            
        self.string = string
        self.character = character
        self.character_end = character_end
        self.filename = None 
    
    def get_substring(self):
        """ Returns the substring to which we refer. Raises error if character_end is None """
        if self.character_end is None:
            msg = 'Character end is None'
            raise_desc(ValueError, msg, where=self)
        return self.string[self.character:self.character_end]
    
    def __repr__(self):
        if self.character_end is not None:
            part = self.string[self.character:self.character_end]
            return 'Where(%r)' % part
        else:
            return 'Where(s=...,char=%s-%s,line=%s,col=%s)' % (self.character, self.character_end, self.line, self.col)

    def with_filename(self, filename):
        if self.character is not  None:
            w2 = Where(string=self.string,
                   character=self.character, character_end=self.character_end)
        else:
            w2 = Where(string=self.string, line=self.line, column=self.col)
        w2.filename = filename
        return w2

    def __str__(self):
        return format_where(self)
        
# mark = 'here or nearby'
def format_where(w, context_before=3, mark=None, arrow=True, 
                 use_unicode=True, no_mark_arrow_if_longer_than=3):
    
    # hack for tabs 
#     w = Where(w.string, w.col, w.col_end)
#     if '\t' in w.string:
#         w.string = w.string.replace('\t', '@') 

    s = ''
    if w.filename:
        s += 'In file %r:\n' % w.filename
    
    
    lines = w.string.split('\n')
    start = max(0, w.line - context_before)
    pattern = 'line %2d |'
    i = 0
    maxi = i + 1
    assert 0 <= w.line < len(lines), (w.character, w.line,  w.string.__repr__())
    
    # skip only initial empty lines - if one was written do not skip
    one_written = False 
    for i in range(start, w.line + 1):
        # suppress empty lines
        if one_written or lines[i].strip():
            lines[i] = lines[i].replace('\t', '@')
            s += ("%s%s\n" % (pattern % (i+1), lines[i]))
            one_written = True
        
    fill = len(pattern % maxi)
    
    # select the space before the string in the same column
    char0 = location(w.line, 0, w.string) # from col 0
    char0_end = location(w.line, w.col, w.string) # to w.col
    space_before = Where(w.string, char0, char0_end)
    
    nindent = printable_length_where(space_before)
    S = ' '
#     print('space_before = %r, nindent = %r' % (space_before, nindent))
     
    #s += '\n' + '~' * fill + '\n'
    space = S * fill + S * nindent
#     print 'column %s, len(space) = %s\n' % (w.col, len(space))
#     s += len(space) * '1' + '\n'
    if w.col_end is not None:
        if w.line == w.line_end:
            num_highlight = printable_length_where(w)
            s += space + '~' * num_highlight + '\n'
            space += S * (num_highlight/2)
        else:
            # cannot highlight if on different lines
            num_highlight = None
            pass
    else:
        num_highlight = None
    # Do not add the arrow and the mark if we have a long underline string 
    
    disable_mark_arrow  = (num_highlight is not None) and (no_mark_arrow_if_longer_than <num_highlight) 
    
    if not disable_mark_arrow:
        if arrow:
            if use_unicode:
                s += space + '↑\n'
            else:
                s += space + '^\n'
                s += space + '|\n'
            
        if mark is not None:
            s += space + mark
        
    s = s.rstrip()
    
#     from .utils import indent
#     s +='\n' + indent(w.string, '> ')
    return s


