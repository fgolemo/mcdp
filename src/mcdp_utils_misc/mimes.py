
from mcdp import logger

def get_mime_for_format(data_format):
    table = get_mime_table()
    if data_format.lower() != data_format:
        logger.error('You should not use uppercase (%s)'  % data_format)
        data_format =data_format.lower()
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