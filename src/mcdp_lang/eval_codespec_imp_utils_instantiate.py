import traceback

from contracts import contract
from contracts.utils import raise_desc, indent
import sys


__all__ = ['import_name', 'instantiate']

class SemanticMistake(Exception):
    pass

def instantiate(function_name, parameters):
    try:
        function = import_name(function_name)
    except ValueError as e:
        msg = 'instantiate(): Cannot find function or constructor %r:\n' % (function_name)
        msg += indent('%s' % (e), '> ')
        raise SemanticMistake(msg)

    try:
        # XXX TypeError is too broad, we should bind the params explicitly
        return function(**parameters)
    except TypeError as e:
        params = ', '.join(['%s=%r' % (k, v) for (k, v) in parameters.items()])
        msg = ('instantiate(): Could not call function %r\n with params %s:' %
               (function_name, params))
        msg += '\n' + indent('%s\n%s' % (e, traceback.format_exc(e)), '> ')
        raise SemanticMistake(msg)

class ImportFailure(ValueError):
    pass

@contract(name='str')
def import_name(name):
    ''' 
        Loads the python object with the given name. 
    
        Note that "name" might be "module.module.name" as well.
    '''
    try:
        return __import__(name, fromlist=['dummy'])
    except ImportError as e:
        # split in (module, name) if we can
        if '.' in name:
            tokens = name.split('.')
            field = tokens[-1]
            module_name = ".".join(tokens[:-1])

            if False:  # previous method
                try:
                    module = __import__(module_name, fromlist=['dummy'])
                except ImportError as e:
                    msg = ('Cannot load %r (tried also with %r):\n' %
                           (name, module_name))
                    msg += '\n' + indent('%s\n%s' % (e, traceback.format_exc(e)), '> ')
                    raise ImportFailure(msg)

                if not field in module.__dict__:
                    msg = 'No field  %r\n' % (field)
                    msg += ' found in %r.' % (module)
                    raise ImportFailure(msg)

                return module.__dict__[field]
            else:
                # other method, don't assume that in "M.x", "M" is a module.
                # It could be a class as well, and "x" be a staticmethod.
                try:
                    module = import_name(module_name)
                except ImportError as e:
                    msg = ('Cannot load %r (tried also with %r):\n' %
                           (name, module_name))
                    msg += '\n' + indent('%s\n%s' % (e, traceback.format_exc(e)), '> ')
                    raise ImportFailure(msg)

                if not field in module.__dict__:
                    msg = 'No field  %r\n' % (field)
                    msg += ' found in %r.' % (module)
                    raise ImportFailure(msg)

                f = module.__dict__[field]

                # "staticmethod" are not functions but descriptors, we need extra magic
                if isinstance(f, staticmethod):
                    return f.__get__(module, None)
                else:
                    return f

        else:
            msg = 'Cannot import name %r.' % (name)
            msg += '\n' + indent(traceback.format_exc(e), '> ')
            raise_desc(ImportFailure, msg, sys_path=sys.path)

