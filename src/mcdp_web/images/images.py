from mcdp_web.utils.response import response_data
from mcdp_cli.plot import png_pdf_from_gg
from mcdp_report.gg_ndp import gvgen_from_ndp
from mcdp_report.gdc import STYLE_GREENREDSYM
from mcdp_web.utils.image_error_catch_imp import png_error_catch
from mocdp.comp.composite_templatize import ndp_templatize
from mcdp_report.report import gvgen_from_dp



class WebAppImages():

    def __init__(self):
        pass

    def config(self, config):

        config.add_route('solver_image',
                         '/libraries/{library}/models/{model_name}/views/solver/compact_graph.png')
        config.add_view(self.view_ndp_graph_templatized, route_name='solver_image')
        config.add_route('solver_image2',
                         '/libraries/{library}/models/{model_name}/views/solver/{fun_axes}/{res_axes}/compact_graph.png')
        config.add_view(self.view_ndp_graph_templatized, route_name='solver_image2')

        config.add_route('solver2_image',
                         '/libraries/{library}/models/{model_name}/views/solver2/compact_graph.png')
        config.add_view(self.view_ndp_graph_templatized, route_name='solver2_image')


        config.add_route('model_ndp_graph_image',
                         self.get_lmv_url('{library}', '{model_name}', 'ndp_graph') +
                         'image/{style}.{format}')
        config.add_view(self.view_model_ndp_graph_image, route_name='model_ndp_graph_image')

        config.add_route('model_dp_graph_image',
                         self.get_lmv_url('{library}', '{model_name}', 'dp_graph') +
                         'image/default.{format}')
        config.add_view(self.view_model_dp_graph_image, route_name='model_dp_graph_image')


    # TODO: catch errors when generating images
    def view_ndp_graph_templatized(self, request):
        """ Returns an image """

        def go():
            l = self.get_library(request)
            id_ndp = self.get_model_name(request)
            ndp = l.load_ndp(id_ndp)

            ndp = ndp_templatize(ndp, mark_as_template=False)

            model_name = self.get_model_name(request)

            images_paths = l.get_images_paths()
            gg = gvgen_from_ndp(ndp, STYLE_GREENREDSYM, yourname=model_name,
                                images_paths=images_paths)
            png, _pdf = png_pdf_from_gg(gg)
            return response_data(request=request, data=png, content_type='image/png')

        return png_error_catch(go, request)

    def view_model_dp_graph_image(self, request):
        def go():
            id_ndp = self.get_model_name(request)
            ndp = self.get_library(request).load_ndp(id_ndp)
            dp = ndp.get_dp()
            gg = gvgen_from_dp(dp)

            png, pdf = png_pdf_from_gg(gg)

            fileformat = request.matchdict['format']

            if fileformat == 'pdf':
                return response_data(request=request, data=pdf, content_type='image/pdf')
            elif fileformat == 'png':
                return response_data(request=request, data=png, content_type='image/png')
            else:
                raise ValueError('No known format %r.' % fileformat)
        return png_error_catch(go, request)

    def view_model_ndp_graph_image(self, request):
        def go():
            id_ndp = self.get_model_name(request)
            style = request.matchdict['style']
            fileformat = request.matchdict['format']

            library = self.get_library(request)
            ndp = library.load_ndp(id_ndp)
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
