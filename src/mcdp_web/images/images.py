# -*- coding: utf-8 -*-
from mcdp_figures import MakeFiguresNDP
from mcdp_report.gg_ndp import gvgen_from_ndp
from mcdp_report.gg_utils import gg_get_format
from mcdp_web.utils.response import response_data
from mocdp.comp.template_for_nameddp import TemplateForNamedDP
from mocdp.exceptions import mcdp_dev_warning


__all__ = ['WebAppImages']

class WebAppImages():

    def __init__(self):
        pass

    def config(self, config):
        config.add_route('solver_image',
                         '/libraries/{library}/models/{model_name}/views/solver/compact_graph.{format}')
        config.add_view(self.view_ndp_graph_templatized, route_name='solver_image')
        config.add_route('solver_image2',
                         '/libraries/{library}/models/{model_name}/views/solver/{fun_axes}/{res_axes}/compact_graph.{format}')
        config.add_view(self.view_ndp_graph_templatized, route_name='solver_image2')

        config.add_route('solver2_image',
                         '/libraries/{library}/models/{model_name}/views/solver2/compact_graph.{format}')
        config.add_view(self.view_ndp_graph_templatized, route_name='solver2_image')
 
        mf = MakeFiguresNDP(None)
        for x in mf.available(): 
            route_name = 'make_figures_%s' % x
            url = self.get_lmv_url('{library}', '{model_name}', 'images') + '{which}.{format}'
            config.add_route(route_name, url)
            config.add_view(self.make_figures, route_name=route_name)
        
        route_name = 'list_views'
        url = self.get_lmv_url('{library}', '{model_name}', 'images')
        config.add_route(route_name, url)
        config.add_view(self.list_views, route_name=route_name, renderer='images/list_views.jinja2')

    def make_figures(self, request): 
        def go():   
            l = self.get_library(request)
            id_ndp = self.get_model_name(request)
            context = l._generate_context_with_hooks()
            ndp = l.load_ndp(id_ndp, context)
    
            mf = MakeFiguresNDP(ndp=ndp, library=l, yourname=id_ndp)
            
            which = str(request.matchdict['which'])
            data_format = str(request.matchdict['format'])
            data = mf.get_figure(which, data_format)
            mime = get_mime_for_format(data_format)
            return response_data(request=request, data=data, content_type=mime)
        return self.png_error_catch2(request, go)
 
    def list_views(self, request):
        available = []
        mf = MakeFiguresNDP(None)
        for x in sorted(mf.available()): 
            data_formats = mf.available_formats(x)
            available.append((x, data_formats))
        return {
            'available': available,
            'navigation': self.get_navigation_links(request),
        }
        
    # TODO: catch errors when generating images
    def view_ndp_graph_templatized(self, request):
        """ Returns an image """
        def go():
            l = self.get_library(request)
            id_ndp = self.get_model_name(request)
            context = l._generate_context_with_hooks()
            ndp = l.load_ndp(id_ndp, context)
            mf = MakeFiguresNDP(ndp=ndp, library=l, yourname=id_ndp)
            data_format = str(request.matchdict['format'])
            data = mf.get_figure('ndp_graph_templatized', data_format)
            mime = get_mime_for_format(data_format)
            return response_data(request=request, data=data, content_type=mime)
        return self.png_error_catch2(request, go)                        

def get_mime_for_format(data_format):
    table = get_mime_table()
    return table[data_format]

def get_mime_table():
    d = {
         'pdf': 'image/pdf',
         'png': 'image/png',
         'jpg': 'image/jpg',
         'dot': 'text/plain',
         'txt': 'text/plain',
         'svg': 'image/svg+xml',
    }
    return d


