#!/usr/bin/env python
from collections import namedtuple
from copy import deepcopy
from mcdp.exceptions import MCDPException, DPSyntaxError, DPSemanticError,\
    DPNotImplementedError
from mcdp.logs import logger
from mcdp_library.specs_def import specs
from mcdp_library_tests.tests import gives_syntax_error, gives_semantic_error,\
    gives_not_implemented_error
from mcdp_utils_misc import create_tmpdir
import os
import shutil
import time

from contracts.utils import indent
from quickapp import QuickApp

from .host_instance import HostInstance
from .library_view import TheContext
from contracts import contract


__all__ = [
    'load_all_main',
]

class LoadAll(QuickApp):
    """ 
    
        Loads all models found in the repo specified.
    
        %prog  -d <directory> [-f <filter>]
    """

    def define_options(self, params):
        params.add_string('dirname', short='-d', help='Directory for the repo.') 
        params.add_string('filter', short='-f', help='Filter for this name.', default=None)
        params.add_flag('errors_only',  help='Only show errored in the summary')

    def define_jobs_context(self, context):
        options = self.get_options()
        
        _filter = options.filter
        errors_only = options.errors_only    
        dirname = options.dirname
        outdir = os.path.join(options.output, 'results')
        
        define_load_all_jobs(context, dirname=dirname, outdir=outdir, name_filter=_filter, errors_only=errors_only)
        
@contract(filter='None|str', errors_only=bool, outdir=str, dirname=str)
def define_load_all_jobs(context, dirname, outdir, name_filter=None, errors_only=False):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    rmtree_only_contents(outdir)

    results = {}
    
    db_view = db_view_from_dirname(dirname)
    
    for e in iterate_all(db_view): 
        if name_filter is not None:
            # case insensitive
            if not name_filter.lower() in e.id.lower():
                continue
        c = context.comp(process, dirname, e, job_id = e.id)
        results[e.id] = (e, c)
    if not results:
        msg = 'Could not find anything to parse. (filter: %s)' % name_filter
        raise Exception(msg)
    context.comp(summary, results, outdir, errors_only)
    context.comp(raise_if_any_error, results)


def raise_if_any_error(results):
    nerrors = 0
    for r in results:
        if r.error_type is not None:
            nerrors += 1
    if nerrors:
        msg = 'Found %s errors' % nerrors
        raise Exception(msg)
        
def rmtree_only_contents(d):
    ''' Removes all the contents but not the directory itself. '''
    
    for the_file in os.listdir(d):
        file_path = os.path.join(d, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): 
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error(e)
            
            
def db_view_from_dirname(dirname):
    instance = 'instance'
    upstream  = 'master'
    root = create_tmpdir('root')
    repo_git = {}
    repo_local = {'local':dirname}
    hi = HostInstance(instance, upstream, root, repo_git, repo_local)
    
    db_view = hi.db_view
    db_view.set_root()
    return db_view


def summary(results, out, errors_only):
    s = ""
    shelf_name = None
    library_name = None
    spec_name = None
    nerrors = 0 
    from termcolor import colored 
    c1 = lambda s: colored(s, color='cyan')
    ce = lambda s: colored(s, color='red')
    cok = lambda s: colored(s, color='green')
    cyellow = lambda s: colored(s, color='yellow')
    cpu = []
    for _ in sorted(results):
        e, result = results[_]
        cpu.append(result.cpu)
        if result.error_type is not None:
            nerrors += 1
        if e.shelf_name != shelf_name:
            shelf_name = e.shelf_name
            s += c1('\n Shelf %s' % shelf_name)
        if e.library_name != library_name:
            library_name = e.library_name
            s += c1('\n   Library %s' % library_name)
        if e.spec_name != spec_name:
            spec_name = e.spec_name
            s += c1('\n     %s' % spec_name)
        if result.error_type:
            s += ce('\n     %20s  %s' % (result.error_type, e.thing_name))
            s += '\n' + indent(result.error_string[:200], '       > ')
        else:
            if not errors_only:
                if result.warnings:
                    warnings = result.warnings
                else:
                    warnings = '' 
                ms = 1000 * result.cpu
                ok = '%dms' % ms
                if ms > 1000:
                    ctime = cyellow
                else:
                    ctime = lambda x:x
                s += ctime('\n     %20s' % ok ) + '   ' + cok('%s   %s' % (e.thing_name, warnings))
                
        if result.error_type:
            fn = os.path.join(out, '%s.txt' % e.id)
            with open(fn, 'w') as f:
                f.write(result.error_string)
            logger.info('wrote %s' % fn)
            
    s += '\n'
    
    s += '\nNumber of errors: %d' % nerrors
    import numpy as np
    s += '\nCPU median: %s ms' % (1000 * np.median(cpu)) 
    print(s)
    fn = os.path.join(out, 'stats.txt')
    with open(fn,'w') as f:
        f.write(s)
    logger.info('wrote %s' % fn)


def process(dirname, e):
    db_view = db_view_from_dirname(dirname)
    e.repo = db_view.repos[e.repo_name]
    e.shelf = e.repo.shelves[e.shelf_name]
    e.library = e.shelf.libraries[e.library_name]
    e.things = e.library.things.child(e.spec_name)
    subscribed_shelves = get_all_shelves(db_view)
    e.context = TheContext(db_view, subscribed_shelves, e.library_name)
    e.mcdp_library = e.context.get_library()
    
    source = e.things[e.thing_name]
    
    t0 = time.clock()
    try:
        context = e.context.child()
        e.mcdp_library.load_spec(e.spec_name, e.thing_name, context=context)
        
        error = None
        error_string = None
        exc = None
    except MCDPException as exc:
#         logger.error('Exception: %s' % exc)
        error = type(exc).__name__
        error_string = str(exc)
        #traceback.format_exc(exc)
    finally:
        cpu = time.clock() - t0
        
    if gives_syntax_error(source):
        if isinstance(exc, DPSyntaxError):
            error = None
            error_string = None
        else:
            error = 'Unexpected'
            error_string = 'Expected DPSyntaxError error, got %s' % type(exc).__name__
            error_string += '\n' + indent(error_string, 'obtained > ')
    elif gives_semantic_error(source):
        if isinstance(exc, DPSemanticError):
            error = None
            error_string = None
        else:
            error = 'Unexpected'
            error_string = 'Expected DPSemanticError error, got %s' % type(exc).__name__
            error_string += '\n' + indent(error_string, 'obtained > ')
    elif gives_not_implemented_error(source):
        if isinstance(exc, DPNotImplementedError):
            error = None
            error_string = None
        else:
            error = 'Unexpected'
            error_string = 'Expected DPNotImplementedError error, got %s' % type(exc).__name__
            error_string += '\n' + indent(error_string, 'obtained > ')
        
    if error:
        logger.error(e.id + ' ' + error)
    
    return Result(error_type=error, error_string=error_string, cpu=cpu, warnings=0)


Result = namedtuple('Result', 'error_type error_string warnings cpu')


class EnvironmentMockup(object):
    pass


def get_all_shelves(db_view):
    subscribed_shelves = list()
    
    for _repo_name, repo in db_view.repos.items():
        for shelf_name, _shelf in repo.shelves.items():
            subscribed_shelves.append(shelf_name)
    return subscribed_shelves


def iterate_all(db_view):
    ''' Yields a sequence of EnvironmentMockup. '''
    e = EnvironmentMockup() 
    for repo_name, repo in db_view.repos.items():
        e.repo_name = repo_name
                        
        for shelf_name, shelf in repo.shelves.items():
            e.shelf_name = shelf_name 
            for library_name, library in shelf.libraries.items():
                e.library_name = library_name 
                for spec_name in specs:
                    e.spec_name = spec_name
                    things = library.things.child(spec_name) 
                    for thing_name, _code in things.items():
                        e.thing_name = thing_name
                        e.id = '%s-%s-%s-%s-%s' % (repo_name, shelf_name, 
                                                   library_name, spec_name, thing_name)
                        yield deepcopy(e) 


mcdp_load_all_main = LoadAll.get_sys_main()


if __name__ == '__main__':
    mcdp_load_all_main()