# -*- coding: utf-8 -*-
from contextlib import contextmanager
from copy import deepcopy
import os
import shutil
import sys

from contracts import contract
from contracts.utils import (check_isinstance, format_obs, raise_desc,
    raise_wrapped)
from mcdp_dp import PrimitiveDP
from mcdp_lang import parse_ndp, parse_poset
from mcdp_posets import Poset
from mocdp import ATTR_LOAD_LIBNAME, ATTR_LOAD_NAME, logger, ATTR_LOAD_REALPATH, \
    get_mcdp_tmp_dir
from mocdp.comp.context import Context, ValueWithUnits
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.template_for_nameddp import TemplateForNamedDP
from mocdp.exceptions import DPSemanticError, mcdp_dev_warning, MCDPExceptionWithWhere

from .utils import memo_disk_cache2
from .utils.locate_files_imp import locate_files


mcdp_dev_warning('move away')
log_duplicates = False

__all__ = [
    'MCDPLibrary',
    'ATTR_LOAD_NAME',
]


class MCDPLibrary():
    """
    
        to document:
        
            '_cached' directory
            
            not case sensitive
            
        delete_cache(): deletes the _cached directory
        
    """

    # These are all the extensions that we care about
    ext_ndps = 'mcdp'
    ext_posets = 'mcdp_poset'
    ext_values = 'mcdp_value'
    ext_templates = 'mcdp_template'
    ext_primitivedps = 'mcdp_primitivedp'
    ext_explanation1 = 'expl1.md'  # before the model
    ext_explanation2 = 'expl2.md'  # after the model
    ext_doc_md = 'md'  # library document

    exts_images = ["png", 'jpg', 'PNG', 'JPG', 'JPEG', 'jpeg']
    all_extensions = [ext_ndps, ext_posets, ext_values, ext_templates, ext_primitivedps,
                      ext_explanation1, ext_explanation2, ext_doc_md] + exts_images

    def __init__(self, cache_dir=None, file_to_contents=None, search_dirs=None,
                 load_library_hooks=None):
        """ 
            IMPORTANT: modify clone() if you add state
        """

        # basename "x.mcdp" -> dict(data, realpath)
        if file_to_contents is None:
            file_to_contents = {}
        self.file_to_contents = file_to_contents
        
        if cache_dir is not None:
            self.use_cache_dir(cache_dir)
        else:
            self.cache_dir = None

        if search_dirs is None:
            search_dirs = []

        self.search_dirs = search_dirs

        if load_library_hooks is None:
            load_library_hooks = []
        self.load_library_hooks = load_library_hooks

    def get_images_paths(self):
        """ Returns a list of paths to search for images assets. """
        dirs = set()
        for basename, d in self.file_to_contents.items():
            ext = os.path.splitext(basename)[1][1:]
            if ext in MCDPLibrary.exts_images:
                dirname = os.path.dirname(d['realpath'])
                dirs.add(dirname)
        return list(dirs)

    def clone(self):
        fields = ['file_to_contents', 'cache_dir', 'search_dirs', 'load_library_hooks']
        contents = {}
        for f in fields:
            if not hasattr(self, f):
                raise ValueError(f)
            contents[f] = deepcopy(getattr(self, f))
        res = MCDPLibrary(**contents)
        res.library_name = getattr(self, 'library_name', None)
        return res

    def use_tmp_cache(self):
        """ Uses a temporary directory as cache. """
        import tempfile
        d = get_mcdp_tmp_dir()
        prefix = 'MCDPLibrary_use_tmp_cache'
        dirname = tempfile.mkdtemp(dir=d, prefix=prefix)
        self.use_cache_dir(dirname)
        
    def use_cache_dir(self, cache_dir):
        try:
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            fn = os.path.join(cache_dir, 'touch')
            if os.path.exists(fn):
                os.unlink(fn)
            with open(fn, 'w') as f:
                f.write('touch')
            os.unlink(fn)
        except Exception:
            logger.debug('Cannot write to folder %r. Not using caches.' % cache_dir)
            self.cache_dir = None
        else:
            self.cache_dir = cache_dir

    def delete_cache(self):
        if self.cache_dir:
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)

    @contract(returns=NamedDP)
    def load_ndp(self, id_ndp, context=None):
        return self._load_generic(id_ndp, MCDPLibrary.ext_ndps,
                                  MCDPLibrary.parse_ndp, context)

    @contract(returns=Poset)
    def load_poset(self, id_poset, context=None):
        return self._load_generic(id_poset, MCDPLibrary.ext_posets,
                                  MCDPLibrary.parse_poset, context)

    @contract(returns=ValueWithUnits)
    def load_constant(self, id_poset, context=None):
        return self._load_generic(id_poset, MCDPLibrary.ext_values,
                                  MCDPLibrary.parse_constant, context)

    @contract(returns=PrimitiveDP)
    def load_primitivedp(self, id_primitivedp, context=None):
        return self._load_generic(id_primitivedp, MCDPLibrary.ext_primitivedps,
                                  MCDPLibrary.parse_primitivedp, context)

    @contract(returns=TemplateForNamedDP)
    def load_template(self, id_ndp, context=None):
        return self._load_generic(id_ndp, MCDPLibrary.ext_templates,
                                  MCDPLibrary.parse_template, context)


    @contract(name=str, extension=str)
    def _load_generic(self, name, extension, parsing_function, context):
        """
            parsing_function takes string, context 
        """
        if context is None:
            context = Context()
        if not isinstance(name, str):
            msg = 'Expected a string for the name.'
            raise_desc(ValueError, msg, name=name)
        filename = '%s.%s' % (name, extension)
        f = self._get_file_data(filename)
        data = f['data']
        realpath = f['realpath']

        current_generation = 3
        
        def actual_load():
            # maybe we should clone
            l = self.clone()
            #logger.debug('Parsing %r' % (name))
            context_mine = Context()
            res = parsing_function(l, data, realpath, context=context_mine)

            setattr(res, ATTR_LOAD_NAME, name)
            return dict(res=res, 
                        context_warnings=context_mine.warnings,
                        generation=current_generation)

        if not self.cache_dir:
            res_data = actual_load()
            cached = False
        else:
            cache_file = os.path.join(self.cache_dir, parsing_function.__name__,
                                      '%s.cached' % name)

            res_data = memo_disk_cache2(cache_file, data, actual_load)
            cached = True
            
            if not isinstance(res_data, dict) or not 'generation' in res_data \
                or res_data['generation'] < current_generation: # outdated cache
                logger.debug('Removing stale cache %r.' % cache_file)
                res_data = actual_load()
                try: 
                    os.unlink(cache_file)
                except Exception:
                    pass
                cached = False
        
        res = res_data['res']
        context_warnings = res_data['context_warnings']

        if False:
            cached = '[Cached]' if cached else ''        
            logger.debug('actual_load(): parsed %r with %d warnings %s' %
                          (name, len(context_warnings), cached))
            
        class JustAHack:
            warnings = context_warnings
            
        msg = 'While loading %r.' % name
        from mcdp_lang.eval_warnings import warnings_copy_from_child_make_nested
        
        warnings_copy_from_child_make_nested(context, JustAHack, msg=msg, where=None)
        
        return res

    def parse_ndp(self, string, realpath=None, context=None):
        """ This is the wrapper around parse_ndp that adds the hooks. """
        result = self._parse_with_hooks(parse_ndp, string, realpath, context)
        return result
    
    def parse_poset(self, string, realpath=None, context=None):
        result = self._parse_with_hooks(parse_poset, string, realpath, context)
        return result
    
    def parse_primitivedp(self, string, realpath=None, context=None):
        from mcdp_lang.parse_interface import parse_primitivedp
        result = self._parse_with_hooks(parse_primitivedp, string, realpath, context)
        return result
    
    def parse_constant(self, string, realpath=None, context=None):
        from mcdp_lang.parse_interface import parse_constant
        result = self._parse_with_hooks(parse_constant, string, realpath, context)
        return result

    def parse_template(self, string, realpath=None, context=None):
        from mcdp_lang.parse_interface import parse_template
        template = self._parse_with_hooks(parse_template, string, realpath, context)
        if hasattr(template, ATTR_LOAD_LIBNAME):
            _prev = getattr(template, ATTR_LOAD_LIBNAME)
            # print('library %r gets something from %r' % (self.library_name, _prev))
        else:
            # print('parsed original template at %s' % self.library_name)
            setattr(template, ATTR_LOAD_LIBNAME, self.library_name)
            setattr(template, ATTR_LOAD_REALPATH, realpath)
        return template

    @contextmanager
    def _sys_path_adjust(self):
        previous = list(sys.path)

        # print('search dirs: %s' % self.search_dirs)
        for d in self.search_dirs:
            sys.path.insert(0, d)

        try:
            yield
        finally:
            sys.path = previous

    def _parse_with_hooks(self, parse_ndp_like, string, realpath, context):
        
        with self._sys_path_adjust(): 
            context_mine = self._generate_context_with_hooks()
            try:
                result = parse_ndp_like(string, context=context_mine)
                from mcdp_lang.eval_warnings import warnings_copy_from_child_add_filename

                if context is not None:                
                    warnings_copy_from_child_add_filename(context, context_mine, realpath)

                return result
            except MCDPExceptionWithWhere as e:
                logger.error('extend_with_filename(%r): seen %s' % (realpath, e))
                _type, _value, traceback = sys.exc_info()
                if e.where is None or e.where.filename is None:
                    if realpath is not None:
                        e = e.with_filename(realpath)
                    else:
                        e = e
                raise e, None, traceback
             
    def _generate_context_with_hooks(self):
        context = Context()
        context.load_ndp_hooks = [self.load_ndp]
        context.load_posets_hooks = [self.load_poset]
        context.load_primitivedp_hooks = [self.load_primitivedp]
        context.load_template_hooks = [self.load_template]
        context.load_library_hooks = [self.load_library]
        return context

    def load_library(self, id_library, context=None):
        errors = []
        for hook in self.load_library_hooks:
            try:
                library = hook(id_library, context)
            except DPSemanticError as e:
                if len(self.load_library_hooks) == 1:
                    raise
                errors.append(e)
                continue

            if self.cache_dir is not None:
                # XXX we should create a new one
                library_name = library.library_name
                new_cache = os.path.join(self.cache_dir, 'sublibrary', library_name)
                library.use_cache_dir(new_cache)
            return library

        msg = 'Could not load library %r.' % id_library
        msg += "\n---\n".join([str(_) for _ in errors])
        raise_desc(DPSemanticError, msg)

    @contract(returns='set(str)')
    def list_ndps(self):
        """ Returns all models defined in this library with .mcdp files. """
        return self._list_with_extension(MCDPLibrary.ext_ndps)

    get_models = list_ndps

    @contract(returns='set(str)')
    def list_posets(self):
        """ Returns all models defined in this library with .mcdp files. """
        return self._list_with_extension(MCDPLibrary.ext_posets)

    @contract(returns='set(str)')
    def list_primitivedps(self):
        """ Returns all models defined in this library with .mcdp files. """
        return self._list_with_extension(MCDPLibrary.ext_primitivedps)

    @contract(returns='set(str)')
    def list_templates(self):
        """ Returns all models defined in this library with .mcdp files. """
        return self._list_with_extension(MCDPLibrary.ext_templates)

    @contract(returns='set(str)')
    def list_values(self):
        return self._list_with_extension(MCDPLibrary.ext_values)

    @contract(ext=str)
    def _list_with_extension(self, ext):
        r = []
        for x in self.file_to_contents:
            assert isinstance(x, str), x.__repr__()
            p = '.' + ext
            if x.endswith(p):
                fn = x.replace(p, '')
                assert isinstance(fn, str), (x, p, fn)
                r.append(fn)
        res = set(r)
        return res

    def file_exists(self, basename):
        for fn in self.file_to_contents:
            if fn.lower() == basename.lower():
                return True
        return False

    @contract(basename=str)
    def _get_file_data(self, basename):
        """ returns dict with data, realpath """

        for fn in self.file_to_contents:
            if fn.lower() == basename.lower():
                match = fn
                break
        else:
            msg = 'Could not find file %r. ' % basename
            ext = os.path.splitext(basename)[1].replace('.', '')
            
            available = sorted(self._list_with_extension(ext),
                               key=lambda x: x.lower())

            if available:
                available = ", ".join(available)
                msg += (" Available files with %r extension: %s." %
                        (ext, available))

            raise_desc(DPSemanticError, msg)
        found = self.file_to_contents[match]
        return found

    @contract(d=str)
    def add_search_dir(self, d):
        check_isinstance(d, str)
        self.search_dirs.append(d)

        if not os.path.exists(d):
            raise_desc(ValueError, 'Directory does not exist', d=d)

        try:
            self._add_search_dir(d)
        except DPSemanticError as e:
            msg = 'Error while adding search dir %r.' % d
            raise_wrapped(DPSemanticError, e, msg, search_dirs=self.search_dirs,
                          compact=True)

    @contract(d=str)
    def _add_search_dir(self, d):
        """ Adds the directory to the search directory list. """

        ignore_patterns = ['/out/', '/out-html/', '/reprep-static/', 'html_resources']

        def should_ignore(f):
            for i in ignore_patterns:
                if i in f:
                    # logger.debug('Ignoring %r because of pattern %r.' % (f, i))
                    return True
            return False

        for ext in MCDPLibrary.all_extensions:
            pattern = '*.%s' % ext
            files_mcdp = locate_files(directory=d, pattern=pattern,
                                      followlinks=True)
            for f in files_mcdp:
                if should_ignore(f):
                    continue
                assert isinstance(f, str)
                self._update_file(f, from_search_dir=d)

    @contract(f=str)
    def _update_file_from_editor(self, f):
        return self._update_file(f, from_search_dir='mcdp-web')
    
    @contract(f=str)
    def _update_file(self, f, from_search_dir=None):
        """ from_search_dir: from whence we arrived at this file. """
        basename = os.path.basename(f)
        check_isinstance(basename, str)
        # This will fail because then in pyparsing everything is unicode
        # import codecs
        # data = codecs.open(f, encoding='utf-8').read()
        data = open(f).read()
        realpath = os.path.realpath(f)
        res = dict(data=data, realpath=realpath, path=f, from_search_dir=from_search_dir)

        strict = False
        if basename in self.file_to_contents:
            realpath1 = self.file_to_contents[basename]['realpath']
            path1 = self.file_to_contents[basename]['path']
            
            expected = from_search_dir == 'mcdp-web'
            if not expected:
                if res['realpath'] == realpath1:
                    msg = 'File %r reached twice.' % basename
                    msg += '\n  now from %s' % from_search_dir
                    msg += '\n prev from %s' % self.file_to_contents[basename]['from_search_dir']
                    if not strict:
                        logger.warning(msg + "\n" +
                                       format_obs(dict(path1=path1,
                                                  path2=res['path'])))
                    else:
                        raise_desc(DPSemanticError, msg,
                                   path1=path1,
                                   path2=res['path'])
    
                else:
                    msg = 'Found duplicated file %r.' % basename
                    if not strict:
                        if log_duplicates:
                            logger.warning(msg + "\n" +
                                           format_obs(dict(path1=realpath1,
                                                      path2=res['realpath'])))
                    else:
                        raise_desc(DPSemanticError, msg,
                                   path1=realpath1,
                                   path2=res['realpath'])

        assert isinstance(basename, str), basename

        self.file_to_contents[basename] = res

    def write_to_model(self, name, data):
        basename = '%s.%s' % (name, MCDPLibrary.ext_ndps)
        self._write_generic(basename, data)

    def write_to_template(self, name, data):
        basename = '%s.%s' % (name, MCDPLibrary.ext_templates)
        self._write_generic(basename, data)

    def write_to_constant(self, name, data):
        basename = '%s.%s' % (name, MCDPLibrary.ext_values)
        self._write_generic(basename, data)

    def write_to_primitivedp(self, name, data):
        basename = '%s.%s' % (name, MCDPLibrary.ext_primitivedps)
        self._write_generic(basename, data)

    def write_to_poset(self, name, data):
        basename = '%s.%s' % (name, MCDPLibrary.ext_posets)
        self._write_generic(basename, data)

    def _write_generic(self, basename, data):
        d = self._get_file_data(basename)
        realpath = d['realpath']
        logger.info('writing to %r' % realpath)
        with open(realpath, 'w') as f:
            f.write(data)
        # reload
        self._update_file_from_editor(realpath)

