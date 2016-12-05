import sys  

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, check_isinstance


class MakeFigures():
    
    def __init__(self, aliases, figure2function):
        self.aliases = aliases
        self.figure2function = figure2function
        
    def available(self):
        return set(self.figure2function) | set(self.aliases)
    
    def available_unique(self):
        return set(self.figure2function)
    
    def available_formats(self, name):
        if not name in self.available():
            raise ValueError(name)
        
        if name in self.aliases:
            name = self.aliases[name]
        k, p = self.figure2function[name]
        try:
            formatter = k(**p)
        except TypeError as e:
            msg = 'Could not instance formatter'
            raise_wrapped(TypeError, e, msg, k=k, p=p, name=name)
        return formatter.available_formats()
    
    
    @contract(name=str, formats='str|seq(str)')
    def get_figure(self, name, formats, **params):
        """ If formats is a str, returns a str.
            If formats is a seq, returns a dictionary format_name -> bytes 
        """
        
        if isinstance(formats, unicode):
            raise ValueError(formats)
        check_isinstance(name, str)
        if not isinstance(formats, str):
            for f in formats:
                check_isinstance(f, str)
        if name in self.aliases:
            name = self.aliases[name]
        
        if not name in self.figure2function:
            msg = 'Invalid figure %r.' % name
            raise ValueError(msg)
        
        k, p0 = self.figure2function[name]
        p = dict()
        p.update(p0)
        p.update(params)
        
        try:
            formatter = k(**p)
        except Exception as e:
            msg = 'Cannot instantiate %r with params %r.' % (name, p)
            raise_wrapped(Exception, e, msg, params=p, exc=sys.exc_info() )
        
        formats0 = (formats,) if isinstance(formats, str) else tuple(sorted(formats))
        
        available = formatter.available_formats()
        for _f in formats0:
            assert len(_f) >= 3, (formats, formats0)
            if not _f in available:
                msg = 'Format %s not provided.' % _f
                raise_desc(ValueError, msg, available=available)
 
        res = formatter.get(self, formats)
        
#         if not isinstance(res, tuple) and len(res) == len(formats):
#             msg = 'Invalid result of %s' % name
#             raise_desc(ValueError, msg, res=res)
#         
        if isinstance(formats, str):
            r = res
            check_isinstance(res, str)
        else:
            r = dict(zip(formats, res)) 
        return r
    

        