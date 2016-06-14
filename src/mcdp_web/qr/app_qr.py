from mcdp_web.utils import response_data
from pyramid.httpexceptions import HTTPFound
import binascii
import os
import traceback


class AppQR():
    def __init__(self):
        self.appqr_reset()

    def config(self, config):

        config.add_route('qr_reader',
                         '/libraries/{library}/qr_reader/')
        config.add_view(self.view_qr_reader, route_name='qr_reader',
                        renderer='qr/qr_reader.jinja2')

        config.add_route('qr_reader_submit',
                         '/libraries/{library}/qr_reader/qr_reader_submit')
        config.add_view(self.qr_reader_submit,
                        route_name='qr_reader_submit', renderer='json')

        config.add_route('scraped',
                         '/libraries/{library}/qr_reader/scraped/{hex}/{num}')
        config.add_view(self.serve_scraped, route_name='scraped')

        config.add_route('qr_import',
                         '/libraries/{library}/qr_reader/qr_import/{hex}')
        config.add_view(self.view_qr_import,
                        route_name='qr_import')

    def view_qr_reader(self, request):  # @UnusedVariable
        return {}

    def appqr_reset(self):
        # qrstring to resources
        self.retrieved = {}
        # qrstring to error message
        self.retrieved_error = {}
        
    def _read(self, qrstring):
        if not (qrstring in self.retrieved) and (not qrstring in self.retrieved_error):
            from mcdp_web.qr.app_qr_scraping import scrape
            try:
                resources = scrape(qrstring)
                self.retrieved[qrstring] = resources
            except Exception as e:
                self.retrieved_error[qrstring] = Exception(traceback.format_exc(e))
            
        if qrstring in self.retrieved:
            return self.retrieved[qrstring]
        if qrstring in self.retrieved_error:
            raise self.retrieved_error[qrstring]
        assert False
            
    def qr_reader_submit(self, request):
        qrstring = request.params['qrstring']
        print(qrstring)
        try:
            resources = self._read(qrstring)

        except Exception as e:
            res = {}
            res['message'] = 'Error occurred'
            s = 'While loading %r:' % qrstring
            s += '\n' + traceback.format_exc(e)
            res['output'] = '<pre><code>' + s + '</code></pre>'
            return res
        else:
            encoded = binascii.hexlify(qrstring)

            output = ''
            output += """
                     <form method="POST" action="qr_import/%s">
                        <input type="submit" value="Import"/>
                      </form>
                    """ % encoded

            for i, r in enumerate(resources):
                if r.type == 'mcdp/icon':
                    path = 'scraped/%s/%s' % (encoded, i)
                    output += '<img src="%s" style="width: 12em"/>' % path

            res = {}
            res['message'] = 'Found %d resources.' % len(resources)
            res['output'] = output
            return res

    def view_qr_import(self, request):
        hexified = request.matchdict['hex']
        qrstring = binascii.unhexlify(hexified)
        resources = self.retrieved[qrstring]

        library = self.get_current_library_name(request)
        path = self.libraries[library]['path']

        where = os.path.join(path, 'imported')
        if not os.path.exists(where):
            os.makedirs(where)

        for r in resources:
            
            if r.type == 'mcdp/icon':
                if r.content_type == 'image/png':
                    extension = 'png'
                elif r.content_type == 'image/jpg':
                    extension = 'jpg'
                else:
                    assert False

            elif r.type == 'mcdp/model':
                if r.content_type == 'text/mcdp':
                    extension = 'mcdp'
                else:
                    msg = 'Expect content-type to be text/mcdp: %s' % r
                    raise ValueError(msg)

            filename = os.path.join(where, '%s.%s' % (r.name, extension))
            print('written %r' % filename)
            with open(filename, 'wb') as f:
                f.write(r.content)
            
        self._refresh_library(request)
        raise HTTPFound('/libraries/%s/list' % library)

    def serve_scraped(self, request):
        hexified = request.matchdict['hex']
        num = int(request.matchdict['num'])

        qrstring = binascii.unhexlify(hexified)
        resource = self.retrieved[qrstring][num]
        return response_data(request=request, data=resource.content,
                             content_type=resource.content_type)

    
