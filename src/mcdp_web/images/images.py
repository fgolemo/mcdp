from mcdp_web.utils.response import response_data
from mcdp_cli.plot import png_pdf_from_gg
from mcdp_report.gg_ndp import gvgen_from_ndp
from mcdp_report.gdc import STYLE_GREENREDSYM
from mcdp_web.utils.image_error_catch_imp import png_error_catch
from mocdp.comp.composite_templatize import ndp_templatize



class WebAppImages():

    def __init__(self):
        pass

    def config(self, config):

        config.add_route('solver_image', '/libraries/{library}/models/{model_name}/views/solver/compact_graph.png')
        config.add_view(self.image, route_name='solver_image')
        config.add_route('solver_image2', '/libraries/{library}/models/{model_name}/views/solver/{fun_axes}/{res_axes}/compact_graph.png')
        config.add_view(self.image, route_name='solver_image2')

        config.add_route('solver2_image', '/libraries/{library}/models/{model_name}/views/solver2/compact_graph.png')
        config.add_view(self.image, route_name='solver2_image')

    # TODO: catch errors when generating images
    def image(self, request):
        """ Returns an image """

        def go():
            l = self.get_library(request)
            id_ndp = self.get_model_name(request)
            ndp = l.load_ndp(id_ndp)
            ndp = ndp_templatize(ndp, mark_as_template=False)

            model_name = self.get_model_name(request)

            # TODO: find a better way
#             setattr(ndp, '_xxx_label', model_name)
            images_paths = l.get_images_paths()
            gg = gvgen_from_ndp(ndp, STYLE_GREENREDSYM, yourname=model_name,
                                images_paths=images_paths)
            png, _pdf = png_pdf_from_gg(gg)
            return response_data(request=request, data=png, content_type='image/png')

        return png_error_catch(go, request)
