from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPFound
from mocdp.exceptions import DPSemanticError, DPSyntaxError
import os

class AppEditor():

    def __init__(self):
        pass

    def config(self, config):
        config.add_route('edit_form', '/edit/{model_name}')
        config.add_view(self.view_edit_form, route_name='edit_form',
                        renderer='edit_form.jinja2')

        config.add_route('edit_submit', '/edit_submit/{model_name}')
        config.add_view(self.view_edit_submit, route_name='edit_submit')

        config.add_route('new_model', '/new_model/{model_name}')
        config.add_view(self.view_new_model, route_name='new_model')





    def view_edit_form(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode

        filename = '%s.mcdp' % model_name
        l = self.get_library()
        f = l._get_file_data(filename)
        source_code = f['data']
        realpath = f['realpath']
        nrows = int(len(source_code.split('\n')) + 6)
        nrows = min(nrows, 25)

        return {'source_code': source_code,
                'model_name': model_name,
                'realpath': realpath,
                'rows': nrows,
                'error': None}


    def view_edit_submit(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode

        # filename = '%s.mcdp' % model_name
        l = self.get_library()
        # f = l._get_file_data(filename)
        # realpath = f['realpath']

        data = str(request.params['source_code'])
        data = data.replace('\r', '')
        # validation:
        try:
            _parsed = l._actual_load(data, realpath=None)
        except (DPSemanticError, DPSyntaxError) as e:
            error = str(e)
            nrows = int(len(data.split('\n')) + 6)
            params = {'source_code': data,
                      'model_name': model_name,
                      'error': error,
                      'rows': nrows}

            return render_to_response('edit_form.jinja2',
                                      params, request=request)

        l.write_to_model(model_name, data)

        raise HTTPFound('/models/%s/syntax' % model_name)


    def view_new_model(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode
        basename = model_name + '.mcdp'
        l = self.get_library()
        if l.file_exists(basename):
            error = 'File %r already exists.' % basename
            return render_to_response('error_model_exists.jinja2',
                                      {'error': error,
                                       'model_name': model_name}, request=request)

        else:
            source = "mcdp {\n\n}"
            filename = os.path.join(self.dirname, basename)
            with open(filename, 'w') as f:
                f.write(source)
            l._update_file(filename)

            raise HTTPFound('/edit/%s' % model_name)


