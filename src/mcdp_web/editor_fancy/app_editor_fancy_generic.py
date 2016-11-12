# -*- coding: utf-8 -*-
import cgi
from collections import defaultdict, namedtuple
import os
import sys

from bs4 import BeautifulSoup
from pyramid.httpexceptions import HTTPFound  # @UnresolvedImport
from pyramid.renderers import render_to_response  # @UnresolvedImport

from contracts.utils import check_isinstance, raise_wrapped, indent
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parse_interface import parse_ndp_eval, parse_ndp_refine, \
    parse_template_eval, parse_template_refine, parse_constant_eval, \
    parse_constant_refine, parse_poset_eval, parse_poset_refine
from mcdp_lang.syntax import Syntax
from mcdp_library import MCDPLibrary
from mcdp_report.gg_ndp import STYLE_GREENREDSYM
from mcdp_report.html import ast_to_html
from mcdp_web.utils import (ajax_error_catch, create_image_with_string,
    format_exception_for_ajax_response, response_image)
from mcdp_web.utils.response import response_data
from mocdp import logger
from mocdp.exceptions import DPInternalError, DPSemanticError, DPSyntaxError
from contracts.interface import format_where


Spec = namedtuple('Spec', 'url_part url_variable extension '
                  ' parse ' # function that returns the object
                            # composition of the following:
                  ' parse_expr ' #  expr = parse_wrap(string, expr)
                  ' parse_refine ' # expr2 = parse_refine(expr, context)
                  ' parse_eval '   # ndp = parse_eval(expr2, context
                  ' load get_png_data write minimal_source_code')


class AppEditorFancyGeneric():

    def __init__(self):

        # library_name x spec ->  dict(text : ndp)
        # self.last_processed2[library_name x spec][text] = ndp
        self.last_processed2 = defaultdict(lambda: dict())

    def config(self, config):
        from mcdp_web.images.images import ndp_template_enclosed

        spec_models = Spec(url_part='models', url_variable='model_name',
                              extension=MCDPLibrary.ext_ndps,
                              parse=MCDPLibrary.parse_ndp,
                              parse_expr=Syntax.ndpt_dp_rvalue,
                              parse_refine=parse_ndp_refine,
                              parse_eval=parse_ndp_eval,
                              load=MCDPLibrary.load_ndp,
                              get_png_data=get_png_data_model,
                              write=MCDPLibrary.write_to_model,
                              minimal_source_code="mcdp {\n\n}")

        spec_templates = Spec(url_part='templates', url_variable='template_name',
                              extension=MCDPLibrary.ext_templates,
                              parse=MCDPLibrary.parse_template,
                              parse_expr=Syntax.template,
                              parse_refine=parse_template_refine,
                              parse_eval=parse_template_eval,
                              load=MCDPLibrary.load_template,
                              get_png_data=ndp_template_enclosed,
                              write=MCDPLibrary.write_to_template,
                              minimal_source_code="template []\n\nmcdp {\n\n}")

        spec_values = Spec(url_part='values', url_variable='value_name',
                           extension=MCDPLibrary.ext_values,
                           parse=MCDPLibrary.parse_constant,
                           parse_expr=Syntax.rvalue,
                           parse_refine=parse_constant_refine,
                           parse_eval=parse_constant_eval,
                           load=MCDPLibrary.load_constant,
                           get_png_data=get_png_data_unavailable,
                           write=MCDPLibrary.write_to_constant,
                           minimal_source_code="0 g")

        spec_posets = Spec(url_part='posets', url_variable='poset_name',
                           extension=MCDPLibrary.ext_posets,
                           parse=MCDPLibrary.parse_poset,
                           parse_expr=Syntax.space,
                           parse_refine=parse_poset_refine,
                           parse_eval=parse_poset_eval,
                           load=MCDPLibrary.load_poset,
                           get_png_data=get_png_data_unavailable,
                           write=MCDPLibrary.write_to_poset,
                           minimal_source_code="finite_poset {\na <= b <= c\n} ")

        self.config_(config, spec_templates)
        self.config_(config, spec_values)
        self.config_(config, spec_posets)
        self.config_(config, spec_models)

    def get_glmv_url(self, library, url_part, model, view):
        url = '/libraries/%s/%s/%s/views/%s/' % (library, url_part, model, view)
        return url

    def config_(self, config, spec):
        """
            what = templates, values, posets
        """
        route = spec.url_part + '_edit_form_fancy'
        url = self.get_glmv_url('{library}', spec.url_part, '{%s}' % spec.url_variable,
                                 'edit_fancy')
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
        url2 = url + 'graph.{data_format}'
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
            return {'ok': True}

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
        return {'source_code': unicode(source_code, 'utf-8'),
                'realpath': realpath,
                spec.url_variable: widget_name,
                'rows': nrows,
                'navigation': self.get_navigation_links(request),

                'ajax_parse': spec.url_part + '_ajax_parse',
                'error': None}

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
        req = {'text': request.json_body['text']}
        library_name = self.get_current_library_name(request)
        key = (library_name, spec, widget_name)

        parse_expr = spec.parse_expr
        parse_refine = spec.parse_refine
        parse_eval = spec.parse_eval
        
        library = self.get_library(request)

        context = library._generate_context_with_hooks()

        def go():
            try:
                parse_tree = parse_wrap(parse_expr, string)[0]
            except DPSemanticError as e:
                msg = 'I only expected a DPSyntaxError'
                raise_wrapped(DPSemanticError, e, msg, exc=sys.exc_info())
            except DPSyntaxError as e:
                # This is the case in which we could not even parse
                res = format_exception_for_ajax_response(e, quiet=(DPSyntaxError,))
                res['highlight'] = html_mark_syntax_error(string, e)
                res['request'] = req
                return res
            
            try:
                class Tmp:
                    parse_tree_interpreted = None
                     
                def postprocess(block):
                    Tmp.parse_tree_interpreted = parse_refine(block, context) 
                    return Tmp.parse_tree_interpreted
                
                
                try:
                    try:
                        highlight = ast_to_html(string,
                                            parse_expr=parse_expr,
                                            complete_document=False,
                                            add_line_gutter=False,
                                            encapsulate_in_precode=False,
                                            add_css=False,
                                            postprocess=postprocess)
                    except DPSemanticError:
                        # Do it again without postprocess
                        highlight = ast_to_html(string,
                                            parse_expr=parse_expr,
                                            complete_document=False,
                                            add_line_gutter=False,
                                            encapsulate_in_precode=False,
                                            add_css=False,
                                            postprocess=None)
                        raise
                    
                    thing = parse_eval(Tmp.parse_tree_interpreted)
                except (DPSemanticError, DPInternalError) as e:
                    highlight_marked = html_mark(highlight, e.where, "semantic_error")
                    self.last_processed2[key] = None  # XXX
                    res = format_exception_for_ajax_response(e, quiet=(DPSemanticError, DPInternalError))
                    res['highlight'] = highlight_marked
                    res['request'] = req
                    return res
                
                self.last_processed2[key] = thing
            except:
                self.last_processed2[key] = None  # XXX
                raise

            warnings = []
            for w in context.warnings:
                # w.msg
                highlight = html_mark(highlight, w.where, "language_warning")
                wheres = format_where(w.where, context_before=0, mark=None, arrow=False, 
                                      use_unicode=True, no_mark_arrow_if_longer_than=3)
                warning = w.msg + '\n\n' + indent(wheres, '   ')
                warnings.append(warning.strip())
    
            # print string.__repr__()
            # print highlight.__repr__()
            
            return {'ok': True, 
                    'highlight': highlight,
                    'language_warnings': "\n\n".join(warnings), 
                    'request': req}

        return ajax_error_catch(go)

    def graph_generic(self, request, spec):
        def go():
            data_format = str(request.matchdict['data_format'])  # unicode
            library = self.get_library(request)
            widget_name = self.get_widget_name(request, spec)
            library_name = self.get_current_library_name(request)
            key = (library_name, spec, widget_name)

            if not key in self.last_processed2:
                l = self.get_library(request)
                thing = spec.load(l, widget_name)
            else:
                thing = self.last_processed2[key]
                if thing is None:
                    return response_image(request, 'Could not parse.')

            data = spec.get_png_data(library, widget_name, thing, data_format=data_format)
            from mcdp_web.images.images import get_mime_for_format
            mime = get_mime_for_format(data_format)
            return response_data(request, data, mime)
        return self.png_error_catch2(request, go)


    def view_new_model_generic(self, request, spec):
        widget_name = self.get_widget_name(request, spec)
        logger.info('New : %r' % widget_name)
        library = self.get_current_library_name(request)

        basename = '%s.%s' % (widget_name, spec.extension)
        l = self.get_library(request)

        url_edit = ('/libraries/%s/%s/%s/views/edit_fancy/' %
                    (library, spec.url_part, widget_name))
        
        if l.file_exists(basename):
            error = 'File %r already exists.' % basename
            template = 'editor_fancy/error_model_exists_generic.jinja2'
            params = {'error': error, 'url_edit': url_edit,
                      'widget_name': widget_name}
            return render_to_response(template, params, request=request)

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

            l._update_file(filename)

            raise HTTPFound(url_edit)

def html_mark(html, where, add_class):
    """ Returns another html string """
    html = '<pre>' + html + '</pre>'
    soup = BeautifulSoup(html, 'lxml')

    elements = soup.find_all("span")
    for e in elements:
        if e.has_attr('where_character'):
            character = int(e['where_character'])
            character_end = int(e['where_character_end'])
            inside = where.character <= character <= character_end <= where.character_end
            if inside:
                e['class'] = e.get('class', []) + [add_class]
        
    pre = soup.body.pre
    s = str(pre)
    s = s.replace('<pre>', '')
    s = s.replace('</pre>', '')
    return s
    
def html_mark_syntax_error(string, e):
    where = e.where
    character = where.character
    first = string[:character]
    rest = string[character:]
    s = "" + first + '<span style="color:red">'+rest + '</span>'
    return s 
    
def get_png_data_unavailable(library, name, x, data_format):  # @UnusedVariable
    s = str(x)
    return create_image_with_string(s, size=(512, 512), color=(0, 0, 255))


def get_png_data_model(library, name, ndp, data_format):  # @UnusedVariable
    from mcdp_web.images.images import ndp_graph_enclosed
    return ndp_graph_enclosed(library, ndp, style=STYLE_GREENREDSYM,
                              yourname=None, data_format=data_format)
