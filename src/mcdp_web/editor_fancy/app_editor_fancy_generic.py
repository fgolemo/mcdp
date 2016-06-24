from collections import defaultdict, namedtuple
from contracts.utils import raise_wrapped
from mcdp_cli.plot import png_pdf_from_gg
from mcdp_lang.syntax import Syntax
from mcdp_library import MCDPLibrary
from mcdp_report.gg_ndp import STYLE_GREENREDSYM, gvgen_from_ndp
from mcdp_report.html import ast_to_html
from mcdp_web.utils import (ajax_error_catch, ajax_error_catch,
    create_image_with_string, format_exception_for_ajax_response,
    format_exception_for_ajax_response, png_error_catch, response_image)
from mcdp_web.utils.image_error_catch_imp import (create_image_with_string,
    png_error_catch, response_image)
from mcdp_web.utils.response import response_data
from mocdp import logger
from mocdp.comp.template_for_nameddp import TemplateForNamedDP
from mocdp.exceptions import DPSemanticError
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
import cgi
import os




Spec = namedtuple('Spec', 'url_part url_variable extension parse_expr parse'
                  ' load get_png_data write minimal_source_code')

class AppEditorFancyGeneric():

    def __init__(self):

        # library_name x spec ->  dict(text : ndp)
        # self.last_processed2[library_name x spec][text] = ndp
        self.last_processed2 = defaultdict(lambda: dict())

    def config(self, config):
        spec_models = Spec(url_part='models', url_variable='model_name',
                              extension=MCDPLibrary.ext_ndps,
                              parse_expr=Syntax.ndpt_dp_rvalue,
                              parse=MCDPLibrary.parse_ndp,
                              load=MCDPLibrary.load_ndp,
                              get_png_data=get_png_data_model,
                              write=MCDPLibrary.write_to_model,
                              minimal_source_code="mcdp {\n\n}")

        spec_templates = Spec(url_part='templates', url_variable='template_name',
                              extension=MCDPLibrary.ext_templates,
                              parse_expr=Syntax.template,
                              parse=MCDPLibrary.parse_template,
                              load=MCDPLibrary.load_template,
                              get_png_data=get_png_data_template,
                              write=MCDPLibrary.write_to_template,
                              minimal_source_code="template []\n\nmcdp {\n\n}")

        spec_values = Spec(url_part='values', url_variable='value_name',
                           extension=MCDPLibrary.ext_values,
                           parse_expr=Syntax.rvalue,
                           parse=MCDPLibrary.parse_constant,
                           load=MCDPLibrary.load_constant,
                           get_png_data=get_png_data_unavailable,
                           write=MCDPLibrary.write_to_constant,
                           minimal_source_code="0 g")

        spec_posets = Spec(url_part='posets', url_variable='poset_name',
                           extension=MCDPLibrary.ext_posets,
                           parse_expr=Syntax.space_expr,
                           parse=MCDPLibrary.parse_poset,
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
        url2 = url + 'graph.png'
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
        return {'source_code': source_code,
                'realpath': realpath,
                spec.url_variable: widget_name,
                'rows': nrows,
                'navigation': self.get_navigation_links(request),

                'ajax_parse': spec.url_part + '_ajax_parse',
                'error': None}

    def get_text_from_request2(self, request):
        """ Gets the 'text' field, taking care of weird
            unicode characters from the browser. """
        string = request.json_body['text']
        # \xa0 is actually non-breaking space in Latin1 (ISO 8859-1), also chr(160).
        # You should replace it with a space.
        string = string.replace(u'\xa0', u' ')

        try:
            string = str(string.decode('utf-8'))
        except UnicodeEncodeError as e:

            string = string.encode('unicode_escape')
            raise_wrapped(Exception, e, 'What', in_ascii=string)

        return string

    def ajax_parse_generic(self, request, spec):
        widget_name = self.get_widget_name(request, spec)
        string = self.get_text_from_request2(request)
        req = {'text': request.json_body['text']}
        library_name = self.get_current_library_name(request)
        key = (library_name, spec, widget_name)

        def go():
            try:
                highlight = ast_to_html(string,
                                        parse_expr=spec.parse_expr,
                                        complete_document=False,
                                        add_line_gutter=False,
                                        encapsulate_in_precode=False,
                                        add_css=False)
                try:

                    l = self.get_library(request)
                    thing = spec.parse(l, string)

                except DPSemanticError as e:

                    self.last_processed2[key] = None  # XXX
                    res = format_exception_for_ajax_response(e, quiet=(DPSemanticError,))
                    res['highlight'] = highlight
                    res['request'] = req
                    return res

                self.last_processed2[key] = thing
            except:
                self.last_processed2[key] = None  # XXX

                raise

            # print string.__repr__()
            # print highlight.__repr__()
            return {'ok': True, 'highlight': highlight, 'request': req}

        return ajax_error_catch(go)

    def graph_generic(self, request, spec):
        def go():
            widget_name = self.get_widget_name(request, spec)
            library_name = self.get_current_library_name(request)
            key = (library_name, spec, widget_name)

            if not key in self.last_processed2:
                l = self.get_library(request)
                thing = spec.load(l, widget_name)
            else:
                thing = self.last_processed2[key]
                if thing is None:
                    return response_image(request, 'Could not parse model.')

            png = spec.get_png_data(widget_name, thing)

            return response_data(request, png, 'image/png')
        return png_error_catch(go, request)


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


def get_png_data_unavailable(name, x):
    s = str(x)
    return create_image_with_string(s, size=(512, 512), color=(0, 0, 255))


def get_png_data_template(name, x):
    assert isinstance(x, TemplateForNamedDP)

    ndp = x.get_template_with_holes()

    setattr(ndp, '_hack_force_enclose', True)

    gg = gvgen_from_ndp(ndp, STYLE_GREENREDSYM, direction='TB')
    png, _pdf = png_pdf_from_gg(gg)
    return png

def get_png_data_model(name, ndp):
    from mocdp.comp.composite import CompositeNamedDP
    if isinstance(ndp, CompositeNamedDP):
        ndp2 = ndp.templatize_children()
        setattr(ndp2, '_hack_force_enclose', True)
    else:
        ndp2 = ndp
        setattr(ndp2, '_xxx_label', name)

    # ndp2 = cndp_get_suitable_for_drawing(model_name, ndp)

    gg = gvgen_from_ndp(ndp2, STYLE_GREENREDSYM, direction='TB')
    png, _pdf = png_pdf_from_gg(gg)

    return png

