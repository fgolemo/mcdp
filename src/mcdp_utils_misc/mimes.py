
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