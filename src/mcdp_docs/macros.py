from string import Template

from mcdp.exceptions import DPSyntaxError
from mcdp.logs import logger
from mcdp_lang_utils import Where, location

from .manual_constants import MCDPManualConstants


__all__ = ['replace_macros']

def replace_macros(s): 
    ''' Replaces strings of the type @@{key} 
    
        It looks in MCDPManualConstants.macros
        
        Also available 
        
            @@{MCDPConstants.name}
    '''   
    macros = MCDPManualConstants.macros
    class MyTemplate(Template):
        delimiter = '@@'
        idpattern = r'[_a-z][\._a-z0-9]*'

        def _invalid(self, mo):
            i = mo.start('invalid')
            lines = self.template[:i].splitlines(True)
            if not lines:
                colno = 1
                lineno = 1
            else:
                colno = i - len(''.join(lines[:-1]))
                lineno = len(lines)
                
            char = location(lineno-1, colno-1, s)
            w = Where(s, char)
            raise DPSyntaxError('Invalid placeholder', where=w)

    class Sub():
        def __init__(self, data):
            self.data = data
        def __getitem__(self, key):
            if key in self.data:
                return self.data[key]
            
            if '.' in key:
                i = key.index('.')
                first, last = key[:i], key[i+1:]
                #print('%s -> %s, %s' % (key, first, last))
                return self[first][last]
            
            raise KeyError(key)
            
    t = MyTemplate(s)
    MyTemplate.idpattern = r'[_a-z][\._a-z0-9]*'
    try:
        s2 = t.substitute(Sub(macros))
    except KeyError as e:
        key = str(e).replace("'","")
        search_for = MyTemplate.delimiter + key
        logger.error('Could not find key %r' % key)
        char = s.index(search_for)
        w = Where(s, char)
        msg = 'Key %r not found - maybe use braces?' % key
        raise DPSyntaxError(msg, where=w)
    return s2 
