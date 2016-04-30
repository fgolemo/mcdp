from conf_tools.utils import locate_files, raise_x_not_found
from contracts import contract
from contracts.utils import raise_desc
from mocdp.comp.context import Context
from mocdp.exceptions import DPSemanticError, DPSyntaxError
from mocdp.lang.parse_actions import parse_ndp
import os

__all__ = ['MCDPLibrary']


class MCDPLibrary():

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
        context = Context()
        def load(load_arg):
            _c, res = self.load_ndp(load_arg)
            return res
        context.load_ndp_hooks = [load]
        try:
            return parse_ndp(data, context=context)
        except (DPSyntaxError, DPSemanticError) as e:
            raise e.with_filename(realpath)

    def _get_file_data(self, basename):
        """ returns dict with data, realpath """
        if not basename in self.file_to_contents:
            raise_x_not_found('file', basename, self.file_to_contents)

        found = self.file_to_contents[basename]
        return found

    def add_search_dir(self, d):
        if not os.path.exists(d):
            raise_desc(ValueError, 'Directory does not exist', d=d)

        import sys
        # XXX: this needs to change
        sys.path.insert(0, d)

        c = self.clone()
        c._add_search_dir(d)
        return c

    def _add_search_dir(self, d):
        """ Adds the directory to the search directory list. """
        files_mcdp = locate_files(directory=d, pattern='*.mcdp', followlinks=True)
        for f in files_mcdp:
            basename = os.path.basename(f)
            data = open(f).read()
            realpath = os.path.realpath(f)
            res = dict(data=data, realpath=realpath)
            self.file_to_contents[basename] = res


