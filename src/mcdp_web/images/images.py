from mcdp_report.gg_ndp import gvgen_from_ndp
from mcdp_report.report import gvgen_from_dp
from mcdp_web.utils.response import response_data
from mocdp.comp.composite_templatize import ndp_templatize
from mocdp.comp.template_for_nameddp import TemplateForNamedDP
from reprep.constants import MIME_PDF, MIME_PNG, MIME_SVG



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

            model_name = self.get_model_name(request)
            png = ndp_graph_templatized(library=l, ndp=ndp,
                                        yourname=model_name, data_format='png')

            return response_data(request=request, data=png, content_type='image/png')

        return self.png_error_catch2(request, go)

    def view_model_dp_graph_image(self, request):
        def go():
            id_ndp = self.get_model_name(request)
            ndp = self.get_library(request).load_ndp(id_ndp)
            dp = ndp.get_dp()
            gg = gvgen_from_dp(dp)

            fileformat = request.matchdict['format']
            data = gg_get_format(gg, fileformat)

            if fileformat == 'pdf':
                return response_data(request=request, data=data, content_type=MIME_PDF)
            elif fileformat == 'png':
                return response_data(request=request, data=data, content_type=MIME_PNG)
            elif fileformat == 'svg':
                return response_data(request=request, data=data, content_type=MIME_SVG)
            else:
                raise ValueError('No known format %r.' % fileformat)
        return self.png_error_catch2(request, go)

    def view_model_ndp_graph_image(self, request):
        def go():
            id_ndp = self.get_model_name(request)
            style = request.matchdict['style']
            fileformat = request.matchdict['format']

            library = self.get_library(request)
            ndp = library.load_ndp(id_ndp)

            data = ndp_graph_normal(library=library, ndp=ndp, style=style,
                                    yourname=id_ndp,
                                    data_format=fileformat)
            return response_data(request, data, get_mime_for_format(fileformat))

        return self.png_error_catch2(request, go)

def get_mime_for_format(data_format):
    d = {
         'pdf': 'image/pdf',
         'png': 'image/png',
         'jpg': 'image/jpg',
         'dot': 'text/plain',
         'svg': 'image/svg+xml',
    }
    return d[data_format]

def ndp_graph_templatized(library, ndp, yourname=None, data_format='png', direction='LR'):
    ndp = ndp_templatize(ndp, mark_as_template=False)
    images_paths = library.get_images_paths()
    from mcdp_report.gdc import STYLE_GREENREDSYM

    gg = gvgen_from_ndp(ndp, STYLE_GREENREDSYM, yourname=yourname,
                        images_paths=images_paths, direction=direction)
    return gg_get_format(gg, data_format)
    
def ndp_graph_normal(library, ndp, style, yourname, data_format, direction='LR'):
    """ This is not enclosed """
    images_paths = library.get_images_paths()
    gg = gvgen_from_ndp(ndp, style, images_paths=images_paths,
                        yourname=yourname, direction=direction)
    return gg_get_format(gg, data_format)

def ndp_graph_enclosed(library, ndp, style, yourname, data_format, direction='TB',
                       enclosed=True):
    """ This templatizes the children. It forces the enclosure if enclosure is True. """
    from mocdp.comp.composite import CompositeNamedDP
    from mocdp.ndp.named_coproduct import NamedDPCoproduct
    from mocdp.comp.composite_templatize import cndp_templatize_children
    from mocdp.comp.composite_templatize import ndpcoproduct_templatize
    if isinstance(ndp, CompositeNamedDP):
        ndp2 = cndp_templatize_children(ndp)
#         /print('setting _hack_force_enclose %r' % enclosed)
        if enclosed:
            setattr(ndp2, '_hack_force_enclose', enclosed)
    elif isinstance(ndp, NamedDPCoproduct):
        ndp2 = ndpcoproduct_templatize(ndp)
    else:
        ndp2 = ndp

    images_paths = library.get_images_paths()
    # we actually don't want the name on top
    yourname = None  # name
    gg = gvgen_from_ndp(ndp2, style, direction=direction,
                        images_paths=images_paths, yourname=yourname)

    return gg_get_format(gg, data_format)

def ndp_template_enclosed(library, name, x, data_format):
    from mcdp_report.gdc import STYLE_GREENREDSYM

    return ndp_template_graph_enclosed(library, x, style=STYLE_GREENREDSYM, yourname=name,
                                       data_format=data_format, direction='TB', enclosed=True)

def ndp_template_graph_enclosed(library, template, style, yourname, data_format, direction, enclosed):
    assert isinstance(template, TemplateForNamedDP)

    ndp = template.get_template_with_holes()

    if enclosed:
        setattr(ndp, '_hack_force_enclose', True)

    images_paths = library.get_images_paths()
    gg = gvgen_from_ndp(ndp, style=style, direction=direction,
                        images_paths=images_paths, yourname=yourname)
    return gg_get_format(gg, data_format)

#
# def ndp_graph_notenclosed(library, ndp, style, yourname, data_format, direction='TB'):
#     """ This templatizes the children and forces the enclosure """
#     from mocdp.comp.composite import CompositeNamedDP
#     from mocdp.ndp.named_coproduct import NamedDPCoproduct
#     from mocdp.comp.composite_templatize import cndp_templatize_children
#     from mocdp.comp.composite_templatize import ndpcoproduct_templatize
#     if isinstance(ndp, CompositeNamedDP):
#         ndp2 = cndp_templatize_children(ndp)
#         # setattr(ndp2, '_hack_force_enclose', True)
#     elif isinstance(ndp, NamedDPCoproduct):
#         ndp2 = ndpcoproduct_templatize(ndp)
#     else:
#         ndp2 = ndp
#
#     images_paths = library.get_images_paths()
#     # we actually don't want the name on top
#     yourname = None  # name
#     gg = gvgen_from_ndp(ndp2, style, direction=direction,
#                         images_paths=images_paths, yourname=yourname)
#
#     return gg_get_format(gg, data_format)

def ndp_graph_expand(library, ndp, style, yourname, data_format, direction='TB'):
    """ This expands the children, forces the enclosure """
    setattr(ndp, '_hack_force_enclose', True)

    images_paths = library.get_images_paths()
    # we actually don't want the name on top
    yourname = None  # name
    gg = gvgen_from_ndp(ndp, style, direction=direction,
                        images_paths=images_paths, yourname=yourname)

    return gg_get_format(gg, data_format)

def gg_get_format(gg, data_format):
    from reprep import Report
    from mcdp_report.gg_utils import gg_figure
    r = Report()
    do_dot = data_format == 'dot'
    do_png = data_format == 'png'
    do_pdf = data_format == 'pdf'
    do_svg = data_format == 'svg'
    gg_figure(r, 'graph', gg, do_dot=do_dot,
              do_png=do_png, do_pdf=do_pdf, do_svg=do_svg)

    if data_format == 'pdf':
        pdf = r.resolve_url('graph_pdf').get_raw_data()
        return pdf
    elif data_format == 'png':
        png = r.resolve_url('graph/graph').get_raw_data()
        return png
    elif data_format == 'dot':
        dot = r.resolve_url('dot').get_raw_data()
        return dot
    elif data_format == 'svg':
        svg = r.resolve_url('graph_svg').get_raw_data()
        return svg
    else:
        raise ValueError('No known format %r.' % data_format)
