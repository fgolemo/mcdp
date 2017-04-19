# -*- coding: utf-8 -*-
from mcdp_figures import MakeFiguresNDP
from mcdp_utils_misc import get_mime_for_format
from mcdp_web.environment import cr2e
from mcdp_web.resource_tree import ResourceThingViewImages, ResourceThingViewImagesOne
from mcdp_web.utils.response import response_data
from mcdp_web.utils0 import add_std_vars_context
from mcdp_web.context_from_env import library_from_env, image_source_from_env


__all__ = ['WebAppImages']

class WebAppImages(object):

    def __init__(self):
        pass

    def config(self, config): 

        config.add_view(self.make_figures, context=ResourceThingViewImagesOne)
        config.add_view(self.list_views, context=ResourceThingViewImages, renderer='images/list_views.jinja2')

    @cr2e
    def make_figures(self, e): 
        which = e.context.which
        data_format= e.context.data_format
         
        def go():
            library = library_from_env(e)
            image_source = image_source_from_env(e)
               
            ndp = library.load_ndp(e.thing_name)
            mf = MakeFiguresNDP(ndp=ndp, image_source=image_source, yourname=e.thing_name)
            data = mf.get_figure(which, data_format)
            mime = get_mime_for_format(data_format)
            return response_data(request=e.request, data=data, content_type=mime)
        return self.png_error_catch2(e.request, go)
 
    @add_std_vars_context
    @cr2e
    def list_views(self, e):  # @UnusedVariable
        available = []
        mf = MakeFiguresNDP(None)
        for x in sorted(mf.available()): 
            data_formats = mf.available_formats(x)
            available.append((x, data_formats))
        return {
            'available': available,
        } 