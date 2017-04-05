import fnmatch
import os

from contracts import contract
from contracts.utils import indent, raise_desc, check_isinstance, raise_wrapped

from mcdp import MCDPConstants
from mcdp_utils_misc import yaml_dump, get_md5, format_list

from .disk_errors import InvalidDiskOperation

class NoSuchDescendant(Exception):
    pass

class ProxyDirectory(object):
    
    @contract(files='dict(str:*)|None', directories='dict(str:*)|None')
    def __init__(self, files=None, directories=None):
        if files is None:
            files = {}
        if directories is None:
            directories = {}
        for k, f in files.items():
            if not isinstance(f, ProxyFile):
                raise ValueError((k, f))
        for k, d in directories.items():
            if not isinstance(d, ProxyDirectory):
                raise ValueError((k, d))

        self._files = files
        self._directories = directories
    
    def get_files(self):
        return self._files
    
    def get_directories(self):
        return self._directories
    
    def hash_code(self):
        codes = []
        for f in sorted(self._files):
            codes.append([f, self._files[f].hash_code()])
        for d in sorted(self._directories):
            codes.append([d, self._directories[d].hash_code()])
        return get_md5(yaml_dump(codes))
    
    def __len__(self):
        return len(self._files) + len(self._directories)
    
    def __getitem__(self, key):
        if key in self._files:
            return self._files[key]
        if key in self._directories:
            return self._directories[key]
        raise KeyError(key)
    
    def __setitem__(self, key, x):
        if isinstance(x, ProxyDirectory):
            self._directories[key] =x
            if key in self._files:
                raise ValueError('duplicated key %r' % key)
        elif isinstance(x, ProxyFile):
            self._files[key] =x
            if key in self._directories:
                raise ValueError('duplicated key %r' % key)
        else:
            msg = 'Cannot set key %r to %r' % (key, x)
            raise ValueError(msg)
    
    def __iter__(self):
        for x in self._files:
            yield x
        for x in self._directories:
            yield x
            
    def items(self):
        for x in self._files.items():
            yield x
        for x in self._directories.items():
            yield x
            
    def to_disk(self, base):
        
        if not os.path.exists(base):
            os.makedirs(base)
            
        for filename, proxy_file in self._files.items():
            fn = os.path.join(base, filename)
            proxy_file.to_disk(fn)
        
        for dirname, proxy_dir in self._directories.items():
            d = os.path.join(base, dirname)
            proxy_dir.to_disk(d)                
    
    @staticmethod
    def from_disk(base):
        ignore_patterns = MCDPConstants.locate_files_ignore_patterns
        
        def should_ignore_resource(x):
            return any(fnmatch.fnmatch(x, ip) for ip in ignore_patterns)
         
        d0 = ProxyDirectory()
        for fn in os.listdir(base):
            if should_ignore_resource(fn):
                continue
            full = os.path.join(base, fn)
            if os.path.isdir(full):
                d0[fn] = ProxyDirectory.from_disk(full)
            else:
                d0[fn] = ProxyFile.from_disk(full)
        return d0
    
    def tree(self, max_levels=1000):
        if max_levels < 0:
            return 'skipping'
        s = ''
        for k in sorted(self._files):
            f = self._files[k]
            MAX = 50
            if k.endswith('yaml'):
                s += '%s' % k
                s += '\n' + indent(f.contents, ' | ') + '\n'
            else: 
                if len(f.contents) < MAX:
                    s += '%r = %r\n' % (k, f.contents)
                else:
                    s += '%s: %d bytes\n' % (k, len(f.contents))
        for k in sorted(self._directories):
            d = self._directories[k]
            s += '%s/\n' % k
            s += indent(d.tree(max_levels-1).rstrip(), '.   ') + '\n' 
        return s

    def recursive_list_files(self):
        ''' Yields a list of basename, ProxyFile '''
        for k, f in self._files.items():
            check_isinstance(f, ProxyFile)
            yield k, f
        for _, d in self._directories.items():
            for k, f in d.recursive_list_files():
                check_isinstance(f, ProxyFile)
                yield k, f

    @contract(prefix='seq(str)')
    def get_descendant(self, prefix):
        try:
            prefix = tuple(prefix)
            if not prefix:
                return self
            else:
                first = prefix[0]
                if first in self._directories:
                    return self._directories[first].get_descendant(prefix[1:])
                elif first in self._files:
                    if len(prefix) > 1:
                        msg = 'Invalid url %r because %r is a file.' % (prefix, first)
                        raise_desc(NoSuchDescendant, msg)
                    else:
                        return self._files[first]
                else:
                    msg = 'Invalid name %r; it is neither a dir or a file.' % first
                    raise_desc(NoSuchDescendant, msg)   
        except NoSuchDescendant as e:
            msg = 'Cannot get the descendant %s:' % prefix.__repr__()
            msg += '\n' + indent(self.tree(), 'self | ')
            raise_wrapped(NoSuchDescendant, e, msg, compact=True)
   
    
    def file_modify(self, name, contents):
        if not name in self._files:
            msg = 'Cannot modify file %r that does not exist.' % name
            raise InvalidDiskOperation(msg)
        self._files[name] = ProxyFile(contents)

    def file_delete(self, name):
        if not name in self._files:
            msg = 'Cannot delete file %r that does not exist.' % name
            raise InvalidDiskOperation(msg)
        del self._files[name]
    
    def file_rename(self, name, name2):
        if not name in self._files:
            msg = 'Cannot rename file %r that does not exist.' % name
            raise InvalidDiskOperation(msg)
        if name2 in self._files or name2 in self._directories:
            msg = 'Cannot rename file %r to %r because %r already exists' % (name, name2)
            raise InvalidDiskOperation(msg)
        self._files[name2] = self._files.pop(name)
        
    def file_create(self, name, contents):
        if name in self._files or name in self._directories:
            msg = 'Cannot create file that already exists  %r.' % name
            raise InvalidDiskOperation(msg)
        self._files[name] = ProxyFile(contents)

    def dir_delete(self, name):
        if not name in self._directories:
            msg = 'Cannot delete directory that does not exist %r.' % name
            raise InvalidDiskOperation(msg)
        del self._directories[name]

    def dir_create(self, name):
        if name in self._directories:
            msg = 'Cannot create directory %s that already exists.' % name
            raise InvalidDiskOperation(msg)
        self._directories[name] = ProxyDirectory()
    
    def dir_rename(self, name, name2):    
        if not name in self._directories:
            msg = ('Cannot rename directory %r to %r if does not exist in %s.' % 
                   (name, name2, format_list(self._directories)))
            raise InvalidDiskOperation(msg)
        if name2 in self._directories:
            msg = ('Cannot rename directory %r to %r if %r already exists' % 
                    (name, name2, name2))
            raise InvalidDiskOperation(msg)
        self._directories[name2] = self._directories.pop(name)


class ProxyFile(object):
    @contract(contents=str)
    def __init__(self, contents):
        self.contents = contents
        
    def hash_code(self):
        return get_md5(self.contents)
    
    @staticmethod
    def from_disk(fn):
        with open(fn, 'r') as f:
            contents = f.read()
        return ProxyFile(contents)
    
    def to_disk(self, fn):
        dn = os.path.dirname(fn)
        if not os.path.exists(dn):
            os.makedirs(dn)
        with open(fn, 'w') as f:
            f.write(self.contents)
        
        