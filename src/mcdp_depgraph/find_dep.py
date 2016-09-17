from collections import namedtuple
from contracts import contract
from contracts.utils import raise_desc
from mcdp_lang.namedtuple_tricks import (
    isnamedtupleinstance, isnamedtuplewhere, recursive_print)
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.syntax import Syntax
from mcdp_library import Librarian, MCDPLibrary
from mocdp.exceptions import DPSemanticError
from mocdp.memoize_simple_imp import memoize_simple
import networkx as nx


@contract(config_dirs='list(str)', maindir='str')
def find_dependencies(config_dirs, maindir, seeds):

    librarian = Librarian()
    for e in config_dirs:
        librarian.find_libraries(e)

    default_library = librarian.get_library_by_dir(maindir)

    fd = FindDependencies(default_library)
    fd.search(seeds)

    res = {}
    res['fd'] = fd
    return res


Entry = namedtuple('Entry', 'libname name')

class EntryNDP(Entry):
    pass

class EntryTemplate(Entry):
    pass

class EntryPoset(Entry):
    pass


types = [
    (EntryPoset, MCDPLibrary.ext_posets),
    (EntryTemplate, MCDPLibrary.ext_templates),
    (EntryNDP, MCDPLibrary.ext_ndps),
]

class FindDependencies():
    def __init__(self, library):
        self.library = library
        self.default_library_name = library.library_name
        self.visited = {}

    def create_graph(self):
        G = nx.DiGraph()

        for n in self.visited:
            G.add_node(n)
        for n, deps in self.visited.items():
            for d in deps:
                G.add_edge(n, d)

        return G

    def __getstate__(self):
        d = dict(**self.__dict__)
        del d['library']
        return d

    @memoize_simple
    def get_library(self, libname):
        print('getting library %r ' % libname)
        return self.library.load_library(libname)

    def search(self, seeds):
        self.stack = []
        for s in seeds:
            entry = self.interpret(libname=None, name=s)
            self.stack.append(entry)

        for s in self.stack:
            print('examining {}'.format(s))
            if s in self.visited:
                print('skipping {}'.format(s))
                continue

            deps = self.get_dependencies(s)
            self.visited[s] = deps
            for d in deps:
                self.stack.append(d)

            print('%s -> %s' % (s, self.visited[s]))

    def get_dependencies(self, s):
        assert isinstance(s, Entry), s
        if isinstance(s, EntryNDP):
            parse_expr = Syntax.ndpt_dp_rvalue
            ext = MCDPLibrary.ext_ndps
        elif isinstance(s, EntryTemplate):
            parse_expr = Syntax.template
            ext = MCDPLibrary.ext_templates
        elif isinstance(s, EntryPoset):
            parse_expr = Syntax.space
            ext = MCDPLibrary.ext_posets
        else:
            raise NotImplementedError(s.__repr__())

        library = self.get_library(s.libname)
        basename = s.name + '.' + ext

        d = library._get_file_data(basename)
        string = d['data']
        x = parse_wrap(parse_expr, string)[0]

        return self.collect_dependencies(s, x)

    def collect_dependencies(self, s, x):
        assert isnamedtuplewhere(x), x
        default_library = s.libname
        print recursive_print(x)
        deps = set()
        CDP = CDPLanguage
        def visit(x):
            if isinstance(x, CDP.LoadNDP):
                if isinstance(x.load_arg, CDP.NDPName):
                    name = x.load_arg.value
                    libname = default_library
                if isinstance(x.load_arg, CDP.NDPNameWithLibrary):
                    libname = x.load_arg.library.value
                    name = x.load_arg.name.value
                d = EntryNDP(libname=libname, name=name)
                deps.add(d)

            if isinstance(x, CDP.LoadPoset):
                if isinstance(x.load_arg, CDP.PosetName):
                    name = x.load_arg.value
                    libname = default_library
                if isinstance(x.load_arg, CDP.PosetNameWithLibrary):
                    libname = x.load_arg.library.value
                    name = x.load_arg.name.value
                d = EntryPoset(libname=libname, name=name)
                deps.add(d)

            if isinstance(x, CDP.LoadTemplate):
                if isinstance(x.load_arg, CDP.TemplateName):
                    name = x.load_arg.value
                    libname = default_library
                if isinstance(x.load_arg, CDP.TemplateNameWithLibrary):
                    libname = x.load_arg.library.value
                    name = x.load_arg.name.value
                d = EntryTemplate(libname=libname, name=name)
                deps.add(d)

        def traverse(x):
            if not isnamedtupleinstance(x):
                return
            else:
                visit(x)
                for _k, v in x._asdict().items():
                    traverse(v)

        traverse(x)

        return deps

    @contract(returns=Entry)
    def interpret(self, libname, name):
        if '.' in name:
            libname, name = tuple(name.split('.'))
        if libname is None:
            libname = self.default_library_name

        library = self.get_library(libname)

        for klass, ext in types:
            basename = name + '.' + ext
            try:
                _fd = library._get_file_data(basename)
            except DPSemanticError:  # not found
                continue

            # assume there is only one
            return klass(libname=libname, name=name)

        msg = 'Could not find {}.{}.'.format(libname, name)
        raise_desc(ValueError, msg)
