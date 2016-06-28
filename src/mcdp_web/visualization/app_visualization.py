from mcdp_cli.plot import png_pdf_from_gg
from mcdp_report.gg_ndp import STYLE_GREENREDSYM, gvgen_from_ndp
from mcdp_report.html import ast_to_html
from mcdp_report.report import gvgen_from_dp
from mcdp_web.utils import png_error_catch, response_data

class AppVisualization():

    def __init__(self):
        pass
    

    def config(self, config):
        config.add_route('model_syntax',
                         self.get_lmv_url('{library}', '{model_name}', 'syntax'))

        config.add_view(self.view_model_syntax, route_name='model_syntax',
                        renderer='visualization/model_syntax.jinja2')

        config.add_route('model_ndp_graph',
                         self.get_lmv_url('{library}', '{model_name}', 'ndp_graph'))

        config.add_view(self.view_model_ndp_graph, route_name='model_ndp_graph',
                        renderer='visualization/model_ndp_graph.jinja2')

        config.add_route('model_ndp_graph_image',
                         self.get_lmv_url('{library}', '{model_name}', 'ndp_graph') +
                         'image/{style}.{format}')
        config.add_view(self.view_model_ndp_graph_image, route_name='model_ndp_graph_image')

        config.add_route('model_dp_graph',
                         self.get_lmv_url('{library}', '{model_name}', 'dp_graph'))
        config.add_view(self.view_model_dp_graph, route_name='model_dp_graph',
                        renderer='visualization/model_dp_graph.jinja2')

        config.add_route('model_dp_graph_image',
                         self.get_lmv_url('{library}', '{model_name}', 'dp_graph') +
                         'image/default.{format}')
        config.add_view(self.view_model_dp_graph_image, route_name='model_dp_graph_image')

        config.add_route('model_ndp_repr',
                         self.get_lmv_url('{library}', '{model_name}', 'ndp_repr'))
        config.add_view(self.view_model_ndp_repr, route_name='model_ndp_repr',
                        renderer='visualization/model_generic_text_content.jinja2')

    def view_model_ndp_graph_image(self, request):
        def go():
            model_name = str(request.matchdict['model_name'])  # unicod
            style = request.matchdict['style']
            fileformat = request.matchdict['format']

            library = self.get_library(request)
            ndp = library.load_ndp(model_name)
            images_paths = library.get_images_paths()
            gg = gvgen_from_ndp(ndp, style, images_paths=images_paths)

            from reprep import Report
            from mcdp_report.gg_utils import gg_figure
            r = Report()
            gg_figure(r, 'graph', gg)
            png = r.resolve_url('graph/graph').get_raw_data()
            pdf = r.resolve_url('graph_pdf').get_raw_data()
            dot = r.resolve_url('dot').get_raw_data()

            if fileformat == 'pdf':
                return response_data(request, pdf, 'image/pdf')
            elif fileformat == 'png':
                return response_data(request, png, 'image/png')
            elif fileformat == 'dot':
                return response_data(request, dot, 'text/plain')
            else:
                raise ValueError('No known format %r.' % fileformat)
        return png_error_catch(go, request)

    def view_model_ndp_graph(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode

        return {'model_name': model_name,
                'views': self._get_views(),
                'current_view': 'ndp_graph',
                'navigation': self.get_navigation_links(request),
                'style': STYLE_GREENREDSYM}

    def view_model_dp_graph_image(self, request):
        def go():
            model_name = str(request.matchdict['model_name'])  # unicod
            fileformat = request.matchdict['format']

            ndp = self.get_library(request).load_ndp2(model_name)
            dp = ndp.get_dp()
            gg = gvgen_from_dp(dp)

            png, pdf = png_pdf_from_gg(gg)

            if fileformat == 'pdf':
                return response_data(request=request, data=pdf, content_type='image/pdf')
            elif fileformat == 'png':
                return response_data(request=request, data=png, content_type='image/png')
            else:
                raise ValueError('No known format %r.' % fileformat)
        return png_error_catch(go, request)

    def view_model_dp_graph(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode


        return {'model_name': model_name,
                'navigation': self.get_navigation_links(request),
                'current_view': 'dp_graph',
                }

    def view_model_ndp_repr(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode

        ndp = self.get_library(request).load_ndp2(model_name)
        ndp_string = ndp.__repr__()
        ndp_string = ndp_string.decode("utf8")

        return {'model_name': model_name,
                'content': ndp_string,
                'navigation': self.get_navigation_links(request),
                'current_view': 'ndp_repr'}


    def view_model_syntax(self, request):

        model_name = str(request.matchdict['model_name'])  # unicode

        filename = '%s.mcdp' % model_name
        l = self.get_library(request)
        f = l._get_file_data(filename)
        source_code = f['data']
        realpath = f['realpath']

        highlight = ast_to_html(source_code,
                                complete_document=False,
                                add_line_gutter=False)
        highlight = self.add_html_links(request, highlight)

        return {'source_code': source_code,
                'highlight': highlight,
                'model_name': model_name,
                'realpath': realpath,
                'navigation': self.get_navigation_links(request),
                'current_view': 'syntax'}

#     def get_link_to_model(self, library, model):
#         return "/library/%s/models/%s/syntax" % (library, model)

    def add_html_links(self, request, frag):
        """ Puts links to the models. """
        library = self.get_current_library_name(request)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(frag, 'html.parser')
        from bs4.element import NavigableString

        # look for links of the type:
        # <span class="FromLibraryKeyword">new</span>
        #     <span class="NDPName"> Actuation_a2_vel</span>
        # </span>

        def break_string(s):
            """ Returns initial ws, middle, final ws. """
            middle = s.strip()
            initial = s[:len(s) - len(s.lstrip())]
            final = s[len(s.rstrip()):]
            assert initial + middle + final == s, (initial, middle, final, s)
            return initial, middle, final

        for tag in soup.select('span.NDPName'):
            initial, middle, final = break_string(tag.string)
            tag.string = ''
            
            name = middle
            href = self.get_lmv_url(library, name, 'syntax')

            attrs = {'class': 'link-to-model', 'href': href, 'target': '_blank'}
            new_tag = soup.new_tag("a", **attrs)
            new_tag.string = name

            tag.append(NavigableString(initial))
            tag.append(new_tag)
            tag.append(NavigableString(final))

            if False:
                # TODO: add this as a feature
                img = '/solver/%s/compact_graph' % name
                attrs = {'src': img, 'class': 'popup'}
                new_tag = soup.new_tag("img", **attrs)
                tag.append(new_tag)


        # Add documentation links for each span 
        # that has a class that finishes in "Keyword"
        def select_tags():
            for tag in soup.select('span'):
                if 'class' in tag.attrs:
                    klass = tag.attrs['class'][0]
                    if 'Keyword' in klass:
                        yield tag
                        
        manual = '/docs/language_notes/'

        for tag in select_tags():
            keyword = tag.attrs['class'][0]
            link = manual + '#' + keyword
            text = tag.string
            tag.string = ''
            attrs = {'class': 'link-to-keyword', 'href': link, 'target': '_blank'}
            new_tag = soup.new_tag("a", **attrs)
            new_tag.string = text
            tag.append(new_tag)
        
        return soup.prettify()


