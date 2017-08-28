from mcdp_utils_xml.add_class_and_style import add_class
from bs4.element import Tag
import traceback
from contracts.utils import check_isinstance
from contracts import contract
from mcdp import logger

# <details open>
#   <summary>Copyright 1999-2014.</summary>
#   <p> - by Refsnes Data. All Rights Reserved.</p>
#   <p>All content and graphics on this web site are the property of the company Refsnes Data.</p>
# </details>


def insert_inset(element, short, long_error, klasses=[]):
    """ Inserts an errored details after element """
    details = Tag(name='details')
#     add_class(details, 'error')
    summary = Tag(name='summary')
    summary.append(short)
    details.append(summary)
    pre = Tag(name='pre')
#     add_class(pre, 'error')
    
    for c in klasses:
        add_class(pre, c)
        add_class(details, c)
        add_class(summary, c)
    pre.append(long_error)
    details.append(pre)
    element.insert_after(details)

@contract(e=BaseException)
def note_error(tag0, e):
    check_isinstance(e, BaseException)
    add_class(tag0, 'errored')
#     logger.error(str(e))  # XXX
#     t = Tag(name='div', attrs={'class': 'error %s' % type(e).__name__})
    short = 'Error'
    long_error = traceback.format_exc(e)
    insert_inset(tag0, short, long_error, ['error', type(e).__name__])

@contract(tag0=Tag, msg=bytes)
def note_error_msg(tag0, msg):
    check_isinstance(msg, bytes)
    add_class(tag0, 'errored')
#     logger.error(str(bytes))  # XXX
    short = 'Error'
    long_error = msg
    insert_inset(tag0, short, long_error, ['error'])

def note_error2(element, short, long_error, other_classes=[]):
    if 'errored' in element.attrs.get('class', ''):
        return 
    add_class(element, 'errored')
    logger.error(short + '\n'+ long_error)
    insert_inset(element, short, long_error, ['error']  + other_classes)
    parent = element.parent
    if not 'style' in parent.attrs:
        parent.attrs['style']= 'display:inline;'

def note_warning2(element, short, long_error, other_classes=[]):
    logger.warning(short + '\n' + long_error)
    insert_inset(element, short, long_error, ['warning']  + other_classes)
