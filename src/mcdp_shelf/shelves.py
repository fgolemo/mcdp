import os

from contracts import contract
from contracts.utils import raise_wrapped, raise_desc
import yaml

from mcdp import MCDPConstants
from mcdp.exceptions import FormatException
from mcdp.logs import logger
from mcdp_library.libraries import find_libraries
from mcdp_utils_misc import indent_plus_invisibles, read_file_encoded_as_utf8, locate_files

from .access import acl_from_yaml


class Shelf():
    ''' 
        A shelf has:
        - a set of libraries
        - a set of access control permissions 
        - a list of dependencies
        - a short description (one line, pure text)
        - a long description (markdown)
        - a list of authors

        - a default directory for creating a new library
    '''
    @contract(dependencies='list(str)', authors='list(str)')
    def __init__(self, acl, dependencies, desc_short, desc_long, libraries, authors, dirname, write_to):
        self.acl = acl
        self.dependencies = dependencies
        self.desc_short = desc_short
        self.desc_long = desc_long
        self.libraries = libraries
        self.authors = authors
        self.dirname = dirname
        self.write_to = write_to

    def get_dependencies(self):
        return self.dependencies

    def get_authors(self):
        return self.authors

    def get_desc_short(self):
        return self.desc_short

    def get_desc_long(self):
        return self.desc_long

    @contract(returns='dict(str:str)')
    def get_libraries_path(self):
        ''' Returns a dict of library name -> dirname '''
        return self.libraries

    def get_acl(self):
        return self.acl

    def update_libraries(self):
        self.libraries = find_libraries(self.dirname)


def shelf_from_directory(dirname):
    ''' Dirname should end in shelf_extension '''
    try:
        return shelf_from_directory_(dirname)
    except ValueError as e:
        msg = 'While reading shelf from %s:' % dirname
        raise_wrapped(FormatException, e, msg, compact=True)
        
def shelf_from_directory_(dirname):
    if not dirname.endswith(MCDPConstants.shelf_extension):
        msg = 'Wrong name for shelf: %r' % dirname
        raise ValueError(msg)

    fn = os.path.join(dirname, MCDPConstants.shelf_desc_file)
    if not os.path.exists(fn):
        msg = 'File %r does not exist.' % fn
        raise ValueError(msg)

    u = read_file_encoded_as_utf8(fn)
    try:
        y = yaml.load(u)
        acl = acl_from_yaml(y.pop('acl', MCDPConstants.default_acl))
        dependencies = y.pop('dependencies', [])
        desc_short = y.pop('desc_short', None)
        desc_long = y.pop('desc_long', None)
        authors = y.pop('authors', [])
        expect_fields = ['acl','desc_short','desc_long','authors']
        if y:
            msg = 'Unknown fields %s; expected %s' % (list(y), expect_fields)
            raise_desc(FormatException, msg, filename=fn, contents=u)
    except:
        msg = 'Cannot parse %s:\n%s' % (fn, indent_plus_invisibles(u))
        logger.error(msg)
        raise

    shelf = Shelf(acl=acl, dependencies=dependencies, desc_short=desc_short,
                  desc_long=desc_long, libraries={}, authors=authors,
                  dirname=dirname, write_to=dirname)
    shelf.update_libraries()
    return shelf


@contract(returns='dict(str:$Shelf)')
def find_shelves(dirname):
    ''' Find shelves underneath the directory. '''
    ds = locate_files(dirname, "*.%s" % MCDPConstants.shelf_extension,
                      followlinks=True,
                      include_directories=True,
                      include_files=False)
    res = {}
    for d in ds:
        name = os.path.splitext(os.path.basename(d))[0]
        res[name] = shelf_from_directory(d)
    return res
