
from mocdp.dp_report.html import ast_to_html
from contracts.utils import raise_wrapped
from mcdp_web.app_solver import ajax_error_catch
from mocdp.lang.parse_actions import parse_ndp

class AppEditorFancy():

    def __init__(self):
        pass

    def config(self, config):

        config.add_route('edit_form_fancy', '/edit_fancy/{model_name}/')
        config.add_view(self.view_edit_form_fancy, route_name='edit_form_fancy',
                        renderer='edit_form_fancy.jinja2')

        config.add_route('ajax_parse', '/edit_fancy/{model_name}/ajax_parse')
        config.add_view(self.ajax_parse, route_name='ajax_parse',
                        renderer='json')

        config.add_route('editor_fancy_save', '/edit_fancy/{model_name}/save')
        config.add_view(self.editor_fancy_save, route_name='editor_fancy_save',
                        renderer='json')

#         config.add_route('editor_fancy_discard', '/edit_fancy/{model_name}/discard')
#         config.add_view(self.editor_fancy_discard, route_name='editor_fancy_discard',
#                         renderer='json')


    def editor_fancy_save(self, request):
        string = self.get_text_from_request(request)
        model_name = self.get_model_name(request)
        def go():
            ndp = parse_ndp(string)
            l = self.get_library()
            l.write_to_model(model_name, string)
            return {'ok': True}

        return ajax_error_catch(go)

    def get_model_name(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode
        return model_name

    def view_edit_form_fancy(self, request):
        model_name = self.get_model_name(request)
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

    def get_text_from_request(self, request):
        """ Gets the 'text' field, taking care of weird
            unicode characters from the browser. """
        string = request.json_body['text']
        # \xa0 is actually non-breaking space in Latin1 (ISO 8859-1), also chr(160).
        # You should replace it with a space.
        string = string.replace(u'\xa0', u' ')

        try:
            string = str(string.decode('utf-8'))
        except UnicodeEncodeError as e:

            string = string.encode('unicode_escape')
            raise_wrapped(Exception, e, 'What', in_ascii=string)

        return string
         
    def ajax_parse(self, request):

        string = self.get_text_from_request(request)


        def go():
            highlight = ast_to_html(string,
                                    complete_document=False,
                                    add_line_gutter=False,
                                    encapsulate_in_precode=False, add_css=False)

            ndp = parse_ndp(string)

            return {'ok': True, 'highlight': highlight, 'request':
                    {'text': request.json_body['text']} }

        return ajax_error_catch(go)
    


