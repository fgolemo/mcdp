# -*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPFound  # @UnresolvedImport
from pyramid.renderers import render_to_response  # @UnresolvedImport

from mocdp.exceptions import DPSemanticError, DPSyntaxError


class AppEditor():

    def __init__(self):
        pass

    def config(self, config):
        config.add_route('edit_form', 
                         self.get_lmv_url('{library}', '{model_name}', 'edit'))

        config.add_view(self.view_edit_form, route_name='edit_form',
                        renderer='editor/edit_form.jinja2')

        config.add_route('edit_submit',
                         self.get_lmv_url('{library}', '{model_name}', 'edit') 
                         + 'submit')

        config.add_view(self.view_edit_submit, route_name='edit_submit')


    def view_edit_form(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode

        filename = '%s.mcdp' % model_name
        l = self.get_library(request)
        f = l._get_file_data(filename)
        source_code = f['data']
        realpath = f['realpath']
        nrows = int(len(source_code.split('\n')) + 6)
        nrows = min(nrows, 25)

        return {'source_code': source_code,
                'model_name': model_name,
                'realpath': realpath,
                'rows': nrows,
                'navigation': self.get_navigation_links(request),
                'error': None}


    def view_edit_submit(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode

        l = self.get_library(request)

        data = str(request.params['source_code'])
        data = data.replace('\r', '')
        # validation:
        try:
            _parsed = l.parse_ndp(data, realpath=None)
        except (DPSemanticError, DPSyntaxError) as e:
            error = str(e)
            nrows = int(len(data.split('\n')) + 6)
            params = {'source_code': data,
                      'model_name': model_name,
                      'error': error,
                      'navigation': self.get_navigation_links(request),
                      'rows': nrows}

            return render_to_response('editor/edit_form.jinja2',
                                      params, request=request)

        l.write_to_model(model_name, data)

        raise HTTPFound('/models/%s/syntax' % model_name)

