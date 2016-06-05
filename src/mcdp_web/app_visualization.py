from mcdp_web.utils import response_data
from mocdp.dp_report.gg_ndp import STYLE_GREENREDSYM
from mocdp.dp_report.html import ast_to_html
from mocdp.dp_report.report import gvgen_from_dp

class AppVisualization():

    def __init__(self):
        pass

    def config(self, config):
        config.add_route('model_syntax', '/models/{model_name}/syntax')
        config.add_view(self.view_model_syntax, route_name='model_syntax',
                        renderer='model_syntax.jinja2')

        config.add_route('model_ndp_graph', '/models/{model_name}/ndp_graph')
        config.add_view(self.view_model_ndp_graph, route_name='model_ndp_graph',
                        renderer='model_ndp_graph.jinja2')

        config.add_route('model_ndp_graph_image', '/models/{model_name}/ndp_graph/image/{style}.{format}')
        config.add_view(self.view_model_ndp_graph_image, route_name='model_ndp_graph_image')

        config.add_route('model_dp_graph', '/models/{model_name}/dp_graph')
        config.add_view(self.view_model_dp_graph, route_name='model_dp_graph',
                        renderer='model_dp_graph.jinja2')

        config.add_route('model_dp_graph_image', '/models/{model_name}/dp_graph/image/default.{format}')
        config.add_view(self.view_model_dp_graph_image, route_name='model_dp_graph_image')

        config.add_route('model_ndp_repr', '/models/{model_name}/ndp_repr')
        config.add_view(self.view_model_ndp_repr, route_name='model_ndp_repr',
                        renderer='model_generic_text_content.jinja2')

    def view_model_ndp_graph_image(self, request):
        model_name = str(request.matchdict['model_name'])  # unicod
        style = request.matchdict['style']
        fileformat = request.matchdict['format']

        from mocdp.dp_report.gg_ndp import gvgen_from_ndp
        from cdpview.plot import png_pdf_from_gg

        _, ndp = self.get_library().load_ndp(model_name)
        gg = gvgen_from_ndp(ndp, style)
        png, pdf = png_pdf_from_gg(gg)

        if fileformat == 'pdf':
            return response_data(request=request, data=pdf, content_type='image/pdf')
        elif fileformat == 'png':
            return response_data(request=request, data=png, content_type='image/png')
        else:
            raise ValueError('No known format %r.' % fileformat)


    def view_model_ndp_graph(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode
        models = self.list_of_models()

        return {'model_name': model_name,
                'models': models,
                'views': self._get_views(),
                'current_view': 'ndp_graph',
                'style': STYLE_GREENREDSYM}

    def view_model_dp_graph_image(self, request):
        model_name = str(request.matchdict['model_name'])  # unicod
        fileformat = request.matchdict['format']

        from cdpview.plot import png_pdf_from_gg

        _, ndp = self.get_library().load_ndp(model_name)
        dp = ndp.get_dp()
        gg = gvgen_from_dp(dp)

        png, pdf = png_pdf_from_gg(gg)

        if fileformat == 'pdf':
            return response_data(request=request, data=pdf, content_type='image/pdf')
        elif fileformat == 'png':
            return response_data(request=request, data=png, content_type='image/png')
        else:
            raise ValueError('No known format %r.' % fileformat)

    def view_model_dp_graph(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode
        models = self.list_of_models()

        return {'model_name': model_name,
                'models': models,
                'views': self._get_views(),
                'current_view': 'dp_graph'}

    def view_model_ndp_repr(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode
        models = self.list_of_models()
        _, ndp = self.get_library().load_ndp(model_name)
        ndp_string = ndp.__repr__()
        ndp_string = ndp_string.decode("utf8")

        return {'model_name': model_name,
                'models': models,
                'views': self._get_views(),
                'content': ndp_string,
                'current_view': 'ndp_repr'}


    def view_model_syntax(self, request):
        models = self.list_of_models()
        model_name = str(request.matchdict['model_name'])  # unicode

        filename = '%s.mcdp' % model_name
        l = self.get_library()
        f = l._get_file_data(filename)
        source_code = f['data']
        realpath = f['realpath']

        highlight = ast_to_html(source_code, complete_document=False)

        return {'source_code': source_code,
                'highlight': highlight,
                'model_name': model_name,
                'realpath': realpath,
                'models': models,
                'views': self._get_views(),
                'current_view': 'syntax'}

    def _get_views(self):
        return ['syntax', 'ndp_graph', 'dp_graph', 'ndp_repr']

