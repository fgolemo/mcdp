# -*- coding: utf-8 -*-
import cgi
from collections import defaultdict
import json
from mcdp import MCDPConstants, logger
from mcdp.exceptions import DPInternalError, DPSemanticError, DPSyntaxError,\
    DPNotImplementedError
from mcdp_lang.suggestions import get_suggestions, apply_suggestions
from mcdp_library.specs_def import specs
from mcdp_report.html import ast_to_html
from mcdp_utils_misc import get_sha1, timeit_wall
from mcdp_web.context_from_env import library_from_env, image_source_from_env
from mcdp_web.environment import cr2e
from mcdp_web.images.images import get_mime_for_format
from mcdp_web.resource_tree import ResourceThingViewEditor, ResourceThingViewEditorParse, ResourceThingViewEditorSave,\
    ResourceThingViewEditorGraph, ResourceThingsNew
from mcdp_web.utils import (ajax_error_catch,
                            format_exception_for_ajax_response, response_image, response_data)
from mcdp_web.utils0 import add_std_vars_context
from mocdp.comp.interfaces import NamedDP

from contracts.utils import check_isinstance
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response

from .html_mark_imp import html_mark, html_mark_syntax_error
from .warnings_unconnected import generate_unconnected_warnings


Privileges=MCDPConstants.Privileges

class AppEditorFancyGeneric(object):

    def __init__(self):
        # library_name x spec ->  dict(text : ndp)
        # self.last_processed2[library_name x spec][text] = ndp
        self.last_processed2 = defaultdict(lambda: dict())

    def config(self, config):
        config.add_view(self.view_edit_form_fancy, 
                        context=ResourceThingViewEditor, 
                        renderer='editor_fancy/edit_form_fancy_generic.jinja2')
        config.add_view(self.ajax_parse, context=ResourceThingViewEditorParse, renderer='json')
        config.add_view(self.save, context=ResourceThingViewEditorSave, renderer='json')
        config.add_view(self.graph_generic, context=ResourceThingViewEditorGraph)
        config.add_view(self.view_new_model_generic, context=ResourceThingsNew, permission=Privileges.WRITE) 
    
    @cr2e
    def save(self, e):
        string = get_text_from_request2(e.request)
        
        def go():
            db_view = e.app.hi.db_view
            library = db_view.repos[e.repo_name].shelves[e.shelf_name].libraries[e.library_name]
            things = library.things.child(e.spec_name)
            things[e.thing_name] = string 
            return {'ok': True, 'saved_string': string}
    
        return ajax_error_catch(go, environment=e)
    
    @cr2e
    def ajax_parse(self, e):
        string = get_text_from_request2(e.request)
        text = e.request.json_body['text'].encode('utf8')
        req = {'text': e.request.json_body['text']}
        text_hash = get_sha1(text)
        key = (e.library_name, e.spec.url_part, e.thing_name, text_hash)

        cache = self.last_processed2

        make_relative = lambda s: self.make_relative(e.request, s)
        library = library_from_env(e)

        def go():
            with timeit_wall('process_parse_request'):
                res = process_parse_request(library, string, e.spec, key, cache, make_relative)
            res['request'] = req
            return res

        return ajax_error_catch(go, environment=e)

    @add_std_vars_context
    @cr2e
    def view_edit_form_fancy(self, e): 
        source_code = e.thing 
        nrows = int(len(source_code.split('\n')) + 6)
        nrows = min(nrows, 25)
    
        source_code = cgi.escape(source_code)
        res = {
            'source_code': unicode(source_code, 'utf-8'),
            'source_code_json': unicode(json.dumps(source_code), 'utf-8'),
#             'realpath': realpath, 
            'rows': nrows,
            'ajax_parse': e.spec.url_part + '_ajax_parse',
            'error': None,
            'url_part': e.spec.url_part,
        }
        return res

    @cr2e
    def graph_generic(self, e):
        data_format = e.context.data_format
        text_hash = e.context.text_hash
        
        def go():
            image_source = image_source_from_env(e)
            library = library_from_env(e)
            
            with timeit_wall('graph_generic', 1.0):
                key = (e.library_name, e.spec.url_part, e.thing_name, text_hash)
    
                if not key in self.last_processed2:
                    logger.error('Cannot find key %s' % str(key))
                    logger.error('keys: %s' % list(self.last_processed2))
                    context = e.library._generate_context_with_hooks()
                    thing = e.spec.load(e.library, e.thing_name, context=context)
                else:
                    thing = self.last_processed2[key]
                    if thing is None:
                        return response_image(e.request, 'Could not parse.')
    
                with timeit_wall('graph_generic - get_png_data', 1.0):
                    data = e.spec.get_png_data(image_source=image_source,
                                               name=e.thing_name, 
                                               thing=thing, 
                                               data_format=data_format,
                                               library=library)
                mime = get_mime_for_format(data_format)
                return response_data(e.request, data, mime)
        return self.png_error_catch2(e.request, go)

    @cr2e
    def view_new_model_generic(self, e):
        new_thing_name = e.context.name
        logger.info('Creating new %r' % new_thing_name)
    
        basename = '%s.%s' % (new_thing_name, e.spec.extension)
        url_edit = '../%s/views/edit_fancy/' % new_thing_name
    
        if new_thing_name in e.things:
            error = 'File %r already exists.' % basename
            template = 'editor_fancy/error_model_exists_generic.jinja2'
            res = {'error': error, 'url_edit': url_edit,
                      'widget_name': new_thing_name, 'root': e.root,
                      'static': 'XXX'} # XXX
            e.request.response.status = 409 # Conflict
            return render_to_response(template, res, request=e.request, response=e.request.response)
        else: 
            source = e.spec.minimal_source_code
            e.things[new_thing_name] = source 
            raise HTTPFound(url_edit)


def process_parse_request(library, string, spec, key, cache, make_relative):
    """ returns a dict to be used as the request,
        or raises an exception """
    from mcdp_report.html import sanitize
    
    parse_expr = spec.parse_expr
    parse_refine = spec.parse_refine
    parse_eval = spec.parse_eval
        
    context0 = library._generate_context_with_hooks()
    try:
        class Tmp:
            string_nospaces_parse_tree_interpreted = None
             
        def postprocess(block):
            try:
                x = parse_refine(block, context0)
            except DPSemanticError:
                x = block
            Tmp.string_nospaces_parse_tree_interpreted = x 
            return x
        
        try:
            highlight = ast_to_html(string,
                                    parse_expr=parse_expr,
                                    add_line_gutter=False,
                                    encapsulate_in_precode=False,
                                    postprocess=postprocess)
            
            thing = parse_eval(Tmp.string_nospaces_parse_tree_interpreted, context0)
            
            if isinstance(thing, NamedDP):
                x = Tmp.string_nospaces_parse_tree_interpreted
                generate_unconnected_warnings(thing, context0, x)

        except DPSyntaxError as e:
            return format_syntax_error2(parse_expr, string, e)
        except (DPSemanticError, DPNotImplementedError) as e:
            highlight_marked = html_mark(highlight, e.where, "semantic_error")
            
            cache[key] = None  # meaning we failed
            res = format_exception_for_ajax_response(e, quiet=(DPSemanticError, DPInternalError))
            res['highlight'] = highlight_marked
            return res
        except DPInternalError:
            raise
        
        cache[key] = thing
    except:
        cache[key] = None  # XXX
        raise
    
    if Tmp.string_nospaces_parse_tree_interpreted:
        xri = Tmp.string_nospaces_parse_tree_interpreted
        highlight, string_with_suggestions = \
            get_suggestions_for_string(highlight, string, xri)
    else:
        string_with_suggestions = None
     
    warnings = []
    for w in context0.warnings:
        if w.where is not None:
            tooltip = w.msg
            highlight = html_mark(highlight, w.where, "language_warning",
                                  tooltip=tooltip)
        warning = w.format_user()
        
        warnings.append(sanitize(warning.strip())) 

    x = ['<div class="language_warning_entry">%s</div>' % w 
         for w in warnings]
    language_warnings_html = "\n".join(x)
                           
    def get_link(specname, libname, thingname):
        spec = specs[specname]
        url0 =  ("/libraries/%s/%s/%s/views/syntax/" %  
                    (libname, spec.url_part, thingname))
        return make_relative(url0)
        
#     highlight2 = add_html_links(highlight, library_name, get_link)
#     print highlight2
    res = {
        'ok': True, 
        'highlight': unicode(highlight, 'utf8'),
        'language_warnings': language_warnings_html, 
        'string_with_suggestions': string_with_suggestions,
    }
    return res
    

def get_suggestions_for_string(highlight, string, xri):
    """ Returns highlight, string_with_suggestions """
    suggestions = get_suggestions(xri)
    string_with_suggestions = apply_suggestions(string, suggestions)
    for where, replacement in suggestions:
        if where.character < where.character_end:
            orig = where.string[where.character:where.character_end]
            if replacement.strip():
                tooltip = 'Aesthetic suggestion: replace “%s” with “%s”.' % (orig, replacement)
                bulb = '\xf0\x9f\x92\xa1'
                tooltip += ' The “%sbeautify” button on the top right does it for you.' % bulb
                klass = "suggestion"
            else:
                tooltip = 'Fix indentation.'
                klass = 'indentation'
        elif where.character == where.character_end:
            if replacement.strip():
                tooltip = 'Add “%s”.' % replacement
                klass = 'suggestion'
            else:
                tooltip = 'Fix indentation.'
                klass = 'indentation'
        highlight = html_mark(highlight, where, klass, tooltip=tooltip)
    return highlight, string_with_suggestions

def format_syntax_error2(parse_expr, string, e):
    from mcdp_report.html import mark_unparsable
    string2, expr, _commented_lines = mark_unparsable(string, parse_expr)
    
    res = format_exception_for_ajax_response(e, quiet=(DPSyntaxError,))
    if expr is not None:
        try:
            html = ast_to_html(string2,    
                               ignore_line=None,
                               add_line_gutter=False, 
                               encapsulate_in_precode=False, 
                               parse_expr=parse_expr,   
                               postprocess=None)
    
            res['highlight'] = html
        except DPSyntaxError:
            assert False, string2
    else:
        res['highlight'] = html_mark_syntax_error(string, e)
     
    return res
    
def get_text_from_request2(request):
    """ Gets the 'text' field, taking care of weird
        unicode characters from the browser. 
    
        Returns a string encoded in utf-8.
    """
    string = request.json_body['text']
    # \xa0 is actually non-breaking space in Latin1 (ISO 8859-1), also chr(160).
    # You should replace it with a space.
    string = string.replace(u'\xa0', u' ')

    check_isinstance(string, unicode)
    string = string.encode('utf-8') 
    return string