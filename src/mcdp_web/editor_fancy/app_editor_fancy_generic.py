# -*- coding: utf-8 -*-
import cgi
from collections import defaultdict, namedtuple
import json
import os

from bs4 import BeautifulSoup
from pyramid.httpexceptions import HTTPFound  # @UnresolvedImport
from pyramid.renderers import render_to_response  # @UnresolvedImport

from contracts import contract
from contracts.utils import check_isinstance, raise_desc
from mcdp import logger
from mcdp.exceptions import DPInternalError, DPSemanticError, DPSyntaxError
from mcdp_utils_misc.string_utils import get_sha1
from mcdp_utils_misc.timing import timeit_wall
from mcdp_lang.parse_interface import (parse_ndp_eval, parse_ndp_refine, 
    parse_template_eval, parse_template_refine, parse_constant_eval, 
    parse_constant_refine, parse_poset_eval, parse_poset_refine)
from mcdp_lang.suggestions import get_suggestions, apply_suggestions
from mcdp_lang.syntax import Syntax
from mcdp_library import MCDPLibrary
from mcdp_report.html import ast_to_html, ATTR_WHERE_CHAR, ATTR_WHERE_CHAR_END
from mcdp_web.utils import (ajax_error_catch,
                            format_exception_for_ajax_response, response_image)
from mcdp_web.utils.response import response_data
from mcdp_web.utils0 import add_other_fields
from mocdp.comp.interfaces import NamedDP

from .image import (get_png_data_model,
    ndp_template_enclosed, get_png_data_unavailable, get_png_data_poset,
    get_png_data_syntax_model)
from .warnings_unconnected import generate_unconnected_warnings 


Spec = namedtuple('Spec', 
                  ' url_part '
                  ' url_variable'
                  ' extension '
                  ' parse ' # function that returns the object.
                            # It is a composition of the following:
                  ' parse_expr ' #  expr = parse_wrap(string, expr)
                  ' parse_refine ' # expr2 = parse_refine(expr, context)
                  ' parse_eval '   # ndp = parse_eval(expr2, context
                  ' load ' # load(name, context)
                  ' get_png_data'
                  ' get_png_data_syntax'
                  ' write minimal_source_code')
specs = {}

spec_models = specs['models'] = Spec(url_part='models', 
                                     url_variable='model_name',
                      extension=MCDPLibrary.ext_ndps,
                      parse=MCDPLibrary.parse_ndp,
                      parse_expr=Syntax.ndpt_dp_rvalue,
                      parse_refine=parse_ndp_refine,
                      parse_eval=parse_ndp_eval,
                      load=MCDPLibrary.load_ndp,
                      get_png_data=get_png_data_model,
                      get_png_data_syntax=get_png_data_syntax_model,
                      write=MCDPLibrary.write_to_model,
                      minimal_source_code="mcdp {\n    \n}")

spec_templates = specs['templates']= Spec(url_part='templates', 
                                          url_variable='template_name',
                      extension=MCDPLibrary.ext_templates,
                      parse=MCDPLibrary.parse_template,
                      parse_expr=Syntax.template,
                      parse_refine=parse_template_refine,
                      parse_eval=parse_template_eval,
                      load=MCDPLibrary.load_template,
                      get_png_data=ndp_template_enclosed,
                      get_png_data_syntax=ndp_template_enclosed,
                      write=MCDPLibrary.write_to_template,
                      minimal_source_code="template []\n\nmcdp {\n    \n}")

spec_values = specs['values'] = Spec(url_part='values', 
                                     url_variable='value_name',
                   extension=MCDPLibrary.ext_values,
                   parse=MCDPLibrary.parse_constant,
                   parse_expr=Syntax.rvalue,
                   parse_refine=parse_constant_refine,
                   parse_eval=parse_constant_eval,
                   load=MCDPLibrary.load_constant,
                   get_png_data=get_png_data_unavailable,
                   get_png_data_syntax=get_png_data_unavailable,
                   write=MCDPLibrary.write_to_constant,
                   minimal_source_code="0 g")

spec_posets =specs['posets']= Spec(url_part='posets', 
                                   url_variable='poset_name',
                   extension=MCDPLibrary.ext_posets,
                   parse=MCDPLibrary.parse_poset,
                   parse_expr=Syntax.space,
                   parse_refine=parse_poset_refine,
                   parse_eval=parse_poset_eval,
                   load=MCDPLibrary.load_poset,
                   get_png_data=get_png_data_poset,
                   get_png_data_syntax=get_png_data_poset,
                   write=MCDPLibrary.write_to_poset,
                   minimal_source_code="poset {\n    \n}")

class AppEditorFancyGeneric():

    def __init__(self):

        # library_name x spec ->  dict(text : ndp)
        # self.last_processed2[library_name x spec][text] = ndp
        self.last_processed2 = defaultdict(lambda: dict())

    def config(self, config):
        self.config_(config, spec_templates)
        self.config_(config, spec_values)
        self.config_(config, spec_posets)
        self.config_(config, spec_models)


    def config_(self, config, spec):
        """
            what = templates, values, posets
        """
        route = spec.url_part + '_edit_form_fancy'
        url = self.get_glmv_url2('{library}', spec.url_part, '{%s}' % spec.url_variable,
                                 'edit_fancy', request=None)
        renderer = 'editor_fancy/edit_form_fancy_generic.jinja2'
        view = lambda req: self.view_edit_form_fancy_generic(req, spec=spec)
        config.add_route(route, url)
        config.add_view(view, route_name=route, renderer=renderer)

        parse = lambda req: self.ajax_parse_generic(req, spec)
        route = spec.url_part + '_ajax_parse'
        url2 = url + 'ajax_parse'
        config.add_route(route, url2)
        config.add_view(parse, route_name=route, renderer='json')

        graph = lambda req: self.graph_generic(req, spec)
        route = spec.url_part + '_graph'
        url2 = url + 'graph.{text_hash}.{data_format}'
        config.add_route(route, url2)
        config.add_view(graph, route_name=route)

        save = lambda req: self.editor_fancy_save_generic(req, spec)
        route = spec.url_part + '_save'
        url2 = url + 'save'
        config.add_route(route, url2)
        config.add_view(save, route_name=route, renderer='json')

        new = lambda req: self.view_new_model_generic(req, spec)
        route = spec.url_part + '_new'
        url2 = '/libraries/{library}/' + spec.url_part + '/new/{%s}' % spec.url_variable
        config.add_route(route, url2)
        config.add_view(new, route_name=route)

    def get_widget_name(self, request, spec):
        widget_name = str(request.matchdict[spec.url_variable])  # unicode
        return widget_name

    def editor_fancy_save_generic(self, request, spec):
        widget_name = self.get_widget_name(request, spec)
        string = self.get_text_from_request2(request)
        def go():
            l = self.get_library(request)
            spec.write(l, widget_name, string)
            return {'ok': True, 'saved_string': string}

        return ajax_error_catch(go)

    def view_edit_form_fancy_generic(self, request, spec):
        widget_name = self.get_widget_name(request, spec)

        filename = '%s.%s' % (widget_name, spec.extension)
        l = self.get_library(request)
        f = l._get_file_data(filename)
        source_code = f['data']
        realpath = f['realpath']
        nrows = int(len(source_code.split('\n')) + 6)
        nrows = min(nrows, 25)

        source_code = cgi.escape(source_code)
        res = {
            'source_code': unicode(source_code, 'utf-8'),
            'source_code_json': unicode(json.dumps(source_code), 'utf-8'),
            'realpath': realpath,
            spec.url_variable: widget_name,
            'rows': nrows,
            'navigation': self.get_navigation_links(request),
            'ajax_parse': spec.url_part + '_ajax_parse',
            'error': None,
            'url_part': spec.url_part,
        }

        add_other_fields(self, res, request)
        return res
    
    def get_text_from_request2(self, request):
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

    def ajax_parse_generic(self, request, spec):
        widget_name = self.get_widget_name(request, spec)
        string = self.get_text_from_request2(request)
        text = request.json_body['text'].encode('utf8')
        req = {'text': request.json_body['text']}
        library_name = self.get_current_library_name(request)
        text_hash = get_sha1(text)
        key = (library_name, spec.url_part, widget_name, text_hash)

        library = self.get_library(request)
        cache = self.last_processed2

        make_relative = lambda s: self.make_relative(request, s)
        def go():
            with timeit_wall('process_parse_request'):
                res = process_parse_request(library, library_name, string, spec, key, cache, make_relative)
            res['request'] = req
            
            return res

        return ajax_error_catch(go)

    def graph_generic(self, request, spec):
        def go():
            with timeit_wall('graph_generic', 1.0):
                data_format = str(request.matchdict['data_format'])  # unicode
                text_hash = str(request.matchdict['text_hash'])
                library = self.get_library(request)
                widget_name = self.get_widget_name(request, spec)
                library_name = self.get_current_library_name(request)
                
                key = (library_name, spec.url_part, widget_name, text_hash)
    
                if not key in self.last_processed2:
                    logger.error('Cannot find key %s' % str(key))
                    logger.error('keys: %s' % list(self.last_processed2))
                    l = self.get_library(request)
                    context = l._generate_context_with_hooks()
                    thing = spec.load(l, widget_name, context=context)
                else:
                    thing = self.last_processed2[key]
                    if thing is None:
                        return response_image(request, 'Could not parse.')
    
                with timeit_wall('graph_generic - get_png_data', 1.0):
                    data = spec.get_png_data(library, widget_name, thing, 
                                             data_format=data_format)
                from mcdp_web.images.images import get_mime_for_format
                mime = get_mime_for_format(data_format)
                return response_data(request, data, mime)
        return self.png_error_catch2(request, go)


    def view_new_model_generic(self, request, spec):
        widget_name = self.get_widget_name(request, spec)
        logger.info('Creating new %r' % widget_name)
        library = self.get_current_library_name(request)

        basename = '%s.%s' % (widget_name, spec.extension)
        l = self.get_library(request)
        url_edit = '../%s/views/edit_fancy/' % widget_name

        if l.file_exists(basename):
            error = 'File %r already exists.' % basename
            template = 'editor_fancy/error_model_exists_generic.jinja2'
            res = {'error': error, 'url_edit': url_edit,
                      'widget_name': widget_name}
            res['root'] = self.get_root_relative_to_here(request)
            return render_to_response(template, res, request=request)

        else:
            path = self.libraries[library]['path']
            source = spec.minimal_source_code
            filename = os.path.join(path, 'created', basename)

            d = os.path.dirname(filename)
            if not os.path.exists(d):
                os.makedirs(d)

            logger.info('Writing to file %r.' % filename)
            with open(filename, 'w') as f:
                f.write(source)

            l._update_file_from_editor(filename)

            raise HTTPFound(url_edit)


@contract(html=bytes, returns=bytes)
def html_mark(html, where, add_class, tooltip=None):
    """ Takes a utf-8 encoded string and returns another html string. 
    
        The tooltip functionality is disabled for now.
    """
    check_isinstance(html, bytes)
    
    html = '<www><pre>' + html + '</pre></www>'
    soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')

    elements = soup.find_all("span")
    
    found = [] 
    
    for e in elements:
        if e.has_attr(ATTR_WHERE_CHAR):
            character = int(e[ATTR_WHERE_CHAR])
            character_end = int(e[ATTR_WHERE_CHAR_END])
            #print (where.character, character, character_end, where.character_end)
            # inside = where.character <= character <= character_end <= where.character_end
            inside = character <= where.character <= where.character_end <= character_end
            if inside:
                found.append(e)
                
    if not found:
        msg = 'Cannot find any html element for this location:\n\n%s' % where
        msg += '\nwhere start: %s end: %s' % (where.character, where.character_end)
        msg += '\nwhere.string = %r' % where.string
        msg += '\n' + html.__repr__()
        raise_desc(DPInternalError, msg)
        
    # find the smallest one
    def e_size(e):
        character = int(e[ATTR_WHERE_CHAR])
        character_end = int(e[ATTR_WHERE_CHAR_END])
        l = character_end - character
        return l
    
    ordered = sorted(found, key=e_size)
        
    e2 = ordered[0]    
    e2['class'] = e2.get('class', []) + [add_class]
    
    if tooltip is not None:
        script = 'show_tooltip(this, %r);' % tooltip
        tooltip_u =  unicode(tooltip, 'utf-8') 
        e2['onmouseover'] = script
        e2['title'] = tooltip_u 
        
    pre = soup.body.www
    s = str(pre)
    s = s.replace('<www><pre>', '')
    s = s.replace('</pre></www>', '')
    assert isinstance(s, str)
    return s
    
def html_mark_syntax_error(string, e):
    where = e.where
    character = where.character
    first = string[:character]
    rest = string[character:]
    s = "" + first + '<span style="color:red">'+rest + '</span>'
    return s 

def process_parse_request(library, library_name, string, spec, key, cache, make_relative):
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
        except (DPSemanticError, DPInternalError) as e:
            highlight_marked = html_mark(highlight, e.where, "semantic_error")
            
            cache[key] = None  # meaning we failed
            res = format_exception_for_ajax_response(e, 
                                quiet=(DPSemanticError, DPInternalError))
            res['highlight'] = highlight_marked
            return res
        
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
    