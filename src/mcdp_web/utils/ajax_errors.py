# -*- coding: utf-8 -*-
import cgi
import traceback

from mcdp.exceptions import DPSemanticError, DPSyntaxError


__all__ = [
    'ajax_error_catch',
    'format_exception_for_ajax_response',
]

def format_exception_for_ajax_response(e, quiet=()):
    s = e.__repr__().decode('ascii', 'ignore')
    from mcdp import logger
    try:
        logger.error('format_exception_for_ajax_response: ' + s)
    except UnicodeEncodeError:
        pass
    res = {}
    res['ok'] = False
    if isinstance(e, quiet):
        s = type(e).__name__ + ': ' + str(e)
    else:
        s = traceback.format_exc(e)
    res['error'] = cgi.escape(s)
    return res

def ajax_error_catch(f, quiet=(DPSyntaxError, DPSemanticError)):
    try:
        return f()
    except Exception as e:
        return format_exception_for_ajax_response(e, quiet=quiet)
