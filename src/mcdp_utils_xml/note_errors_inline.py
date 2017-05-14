from mcdp_utils_xml.add_class_and_style import add_class
from bs4.element import Tag
import traceback
from contracts.utils import check_isinstance
from contracts import contract

@contract(e=BaseException)
def note_error(tag0, e):
    check_isinstance(e, BaseException)
    add_class(tag0, 'errored')
#     logger.error(str(e))  # XXX
    t = Tag(name='pre', attrs={'class': 'error %s' % type(e).__name__})
    t.string = traceback.format_exc(e)
    tag0.insert_after(t) 

@contract(tag0=Tag, msg=bytes)
def note_error_msg(tag0, msg):
    check_isinstance(msg, bytes)
    add_class(tag0, 'errored')
#     logger.error(str(bytes))  # XXX
    t = Tag(name='pre', attrs={'class': 'error'})
    t.string = msg
    tag0.insert_after(t) 
