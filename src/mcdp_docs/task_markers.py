from bs4.element import NavigableString

from mcdp import logger
from mcdp_utils_xml import add_class


def substitute_task_markers(soup):
    subs2class = {
        '(TODO)': 'status-todo',
        '(DONE)': 'status-done',
        '(IN PROGRESS)': 'status-inprogress',
        'XXX': 'status-XXX',
        '???': 'status-XXX',
    } 
    
    for sub, klass in subs2class.items():
        substitute_task_marker(soup, sub, klass)
        
def substitute_task_marker(soup, sub, klass):
    ps = list(soup.select('p')) + list(soup.select('h2'))  + list(soup.select('h3'))
    for p in ps:
        substitute_task_marker_p(p, sub, klass)

def substitute_task_marker_p(p, sub, klass):
#     try:
        for element in list(p.descendants): # use list() otherwise modifying 
            if not isinstance(element, NavigableString):
                continue
    
            s = element.string
            if sub in s:
                add_class(p, klass)
#                 s2 = s.replace(sub, '')
#                 ns = NavigableString(s2)
#                 element.replaceWith(ns)
#     except AttributeError as e: # a bug with bs4
#         msg = 'Bug with descendants: %s' % e
#         logger.debug(msg)
#         pass