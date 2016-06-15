from contracts import contract
from contracts.utils import indent
from .eval_codespec_imp_utils_instantiate import instantiate
import traceback

__all__ = [
    'check_valid_code_spec',
    'instantiate_spec',
    'format_code_spec',
    'format_yaml',
]



class InstantiationException(Exception):
    pass


def check_valid_code_spec(x):
    if not isinstance(x, list):
        raise InstantiationException(x, 'A code spec must be a list.')

    if len(x) != 2:
        msg = 'A code spec must be a list of exactly two elements.'
        raise InstantiationException(x, msg)

    name = x[0]
    params = x[1]
    if not isinstance(name, str):
        raise InstantiationException(x, 'The code must be given as a string.')
    if not isinstance(params, dict):
        raise InstantiationException(x, 'The params must be given as a dictionary.')


@contract(code_spec='code_spec')
def instantiate_spec(code_spec):
    ''' code_spec must be a sequence  [string, dictionary], giving
        the python function (or class) to instantiate, along
        with its parameters. '''
    try:
        function_name = code_spec[0]
        parameters = code_spec[1]
        assert isinstance(function_name, str)
        assert isinstance(parameters, dict)

        return instantiate(function_name, parameters)
    except Exception as e:
        msg = 'Could not instance the spec:\n'
        msg += indent(format_code_spec(code_spec).strip(), '  ').strip()
        msg += '\nbecause of this error:\n'
        if isinstance(e, InstantiationException):
            st = str(e)
        else:
            st = traceback.format_exc(e)
        msg += indent(st.strip(), '| ')
        msg = msg.strip()
        raise InstantiationException(msg)

def format_code_spec(code_spec):
    return format_yaml(code_spec)

def format_yaml(ob):
    import yaml
    return yaml.dump(ob)
