from pyramid.response import FileResponse  # @UnresolvedImport

def response_data(request, data, content_type):
    import tempfile
    with tempfile.NamedTemporaryFile() as tf:
        fn = tf.name
        with open(fn, 'wb') as f:
            f.write(data)
        response = FileResponse(fn, request=request, content_type=content_type)

    return response
