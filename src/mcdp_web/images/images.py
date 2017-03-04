# -*- coding: utf-8 -*-
from mcdp_figures import MakeFiguresNDP
from mcdp_utils_misc import get_mime_for_format
from mcdp_web.utils.response import response_data
from mcdp_web.utils0 import add_std_vars_context
from mcdp_web.resource_tree import ResourceThingViewImages, context_get_library,\
    context_get_widget_name, ResourceThingViewImagesOne



__all__ = ['WebAppImages']

class WebAppImages():

    def __init__(self):
        pass

    def config(self, config): 

        config.add_view(self.make_figures, context=ResourceThingViewImagesOne)
        config.add_view(self.list_views, context=ResourceThingViewImages, renderer='images/list_views.jinja2')

    def make_figures(self, context, request):
        which = context.which
        data_format= context.data_format
         
        def go():   
            library = context_get_library(context, request)
            id_ndp = context_get_widget_name(context)
            mycontext = library._generate_context_with_hooks()
            ndp = library.load_ndp(id_ndp, mycontext)
    
            mf = MakeFiguresNDP(ndp=ndp, library=library, yourname=id_ndp)
            data = mf.get_figure(which, data_format)
            mime = get_mime_for_format(data_format)
            return response_data(request=request, data=data, content_type=mime)
        return self.png_error_catch2(request, go)
 
    @add_std_vars_context
    def list_views(self, context, request):  # @UnusedVariable
        available = []
        mf = MakeFiguresNDP(None)
        for x in sorted(mf.available()): 
            data_formats = mf.available_formats(x)
            available.append((x, data_formats))
        return {
            'available': available,
        } 