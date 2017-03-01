from mcdp_utils_xml.add_class_and_style import add_class
from mcdp import logger
from bs4.element import Tag
import traceback

def note_error(tag0, e):
    add_class(tag0, 'errored')
    logger.error(str(e))  # XXX
    t = Tag(name='pre', attrs={'class': 'error %s' % type(e).__name__})
    t.string = traceback.format_exc(e)
    tag0.insert_after(t) 
