
from contracts.utils import raise_desc
from mcdp_hdb.exceptions import IncorrectFormat, NotKey

class HintExtensions(object):
    
    def __init__(self, extensions):
        self.extensions = extensions

    def __repr__(self):
        return 'HintExtensions(%r)' % self.extensions
     
class HintFile(object):
     
    def __init__(self):
        pass
 
    def __repr__(self):
        return 'HintFile()'  
            
class HintDir(object):
    
    def __init__(self, pattern='%', translations=None):
        self.pattern = pattern
        if translations is None:
            translations = {}
        self.translations = translations
 
    def __repr__(self):
        return 'HintDir(%r, %r)' % (self.pattern, self.translations)
    
    def filename_for_key(self, key):
        if key in self.translations:
            return self.translations[key]
        else:
            return self.pattern.replace('%', key)

    def key_from_filename(self, filename):
        pattern = self.pattern
        if not '%' in pattern:
            msg = 'Cannot get key from filename.'
            raise_desc(IncorrectFormat, msg, pattern=pattern, filename=filename)
            
        if pattern.startswith('%'):
            key = filename.replace(pattern.replace('%', ''), '')
            
            filename2 = pattern.replace('%', key)
            if filename2 != filename:
                msg = 'Filename "%s" does not follow pattern "%s".' % (filename, pattern)
                raise NotKey(msg)
            return key
        else:
            raise NotImplementedError(pattern)
        
class HintFileYAML(object):
    def __init__(self):
        pass
        
    def __repr__(self):
        return 'HintFileYAML()'
        