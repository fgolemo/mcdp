# -*- coding: utf-8 -*-
from contracts.utils import raise_wrapped
from contracts import contract
import os

__all__ = [
    'dir_from_package_name',
]


@contract(d='str')
def dir_from_package_name(d):
    """ This works for "package.sub" format. If it's only
        package, we look for __init__.py"""
    tokens = d.split('.')
    if len(tokens) == 1:
        package = d
        sub = '__init__'
    else:
        package = '.'.join(tokens[:-1])
        sub = tokens[-1]
    try:
        from pkg_resources import resource_filename  # @UnresolvedImport
        res = resource_filename(package, sub + '.py')

        if len(tokens) == 1:
            res = os.path.dirname(res)

        return res
    except BaseException as e: # pragma: no cover
        raise_wrapped(ValueError, e, 'Cannot resolve package name', d=d)
