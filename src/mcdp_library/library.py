from .utils.locate_files_imp import locate_files
from contracts import contract
from contracts.utils import raise_desc
from mcdp_library.utils.memos_selection import memo_disk_cache2
from mocdp import logger
from mocdp.comp.context import Context
from mocdp.exceptions import DPSemanticError, DPSyntaxError
from mocdp.lang.parse_actions import parse_ndp
import os
import warnings



__all__ = [
    'MCDPLibrary',
]


class MCDPLibrary():
    """
    
        to document:
        
            '_cached' directory
            
            not case sensitive
        
    """
    def __init__(self, file_to_contents=None):
        # "x.mcdp" -> string
        if file_to_contents is None:
            file_to_contents = {}
        self.file_to_contents = file_to_contents
        self.file_to_realpath = {}
        
    def clone(self):
        fields = ['file_to_contents']
        contents = {}
        for f in fields:
            if not hasattr(self, f):
                raise ValueError(f)
            contents[f] = getattr(self, f).copy()
        return MCDPLibrary(**contents)

    @contract(returns='tuple(*, isinstance(NamedDP))')
    def load_ndp(self, id_ndp):
        c = self.clone()
        res = c._load_ndp(id_ndp)
        return c, res

    def _load_ndp(self, id_ndp):
        filename = '%s.mcdp' % id_ndp
        f = self._get_file_data(filename)
        data = f['data']
        realpath = f['realpath']

        def actual_load():
            logger.debug('Parsing %r' % id_ndp)
            return self._actual_load(data, realpath)

        cache_file = os.path.join('_cached', '%s.cached' % id_ndp)
        return memo_disk_cache2(cache_file, data, actual_load)

    def _actual_load(self, data, realpath=None):
        def load(load_arg):
            _c, res = self.load_ndp(load_arg)
            return res

        context = Context()
        context.load_ndp_hooks = [load]
        try:
            result = parse_ndp(data, context=context)
        except (DPSyntaxError, DPSemanticError) as e:
            if realpath is not None:
                raise e.with_filename(realpath)
            else:
                raise e
        return result

    @contract(returns='set(str)')
    def get_models(self):
        """ Returns all models (files *mcdp) """
        r = []
        for x in self.file_to_contents:
            if x.endswith('.mcdp'):
                r.append(x.replace('.mcdp', ''))
        return set(r)

    def _get_file_data(self, basename):
        """ returns dict with data, realpath """

        for fn in self.file_to_contents:
            if fn.lower() == basename.lower():
                match = fn
                break
        else:
            raise_desc(DPSemanticError, 'Could not find model in library.',
                       model_name=basename, contents=sorted(self.file_to_contents))
        found = self.file_to_contents[match]
        return found

    def add_search_dir(self, d):
        if not os.path.exists(d):
            raise_desc(ValueError, 'Directory does not exist', d=d)

        import sys
        # XXX: this needs to change
        warnings.warn('sys.path hack needs to change')
        sys.path.insert(0, d)

        c = self.clone()
        c._add_search_dir(d)
        return c

    def _add_search_dir(self, d):
        """ Adds the directory to the search directory list. """
        files_mcdp = locate_files(directory=d, pattern='*.mcdp', followlinks=True)
        for f in files_mcdp:
            self._update_file(f)
            
    def _update_file(self, f):
        basename = os.path.basename(f)
        data = open(f).read()
        realpath = os.path.realpath(f)
        res = dict(data=data, realpath=realpath)
        self.file_to_contents[basename] = res

    def write_to_model(self, model_name, data):
        basename = model_name + '.mcdp'
        d = self._get_file_data(basename)
        realpath = d['realpath']
        print('writing to %r' % realpath)
        with open(realpath, 'w') as f:
            f.write(data)
        # reload
        self._update_file(realpath)
        
