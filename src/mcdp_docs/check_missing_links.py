from mcdp.logs import logger
from mcdp_utils_xml.add_class_and_style import add_class
from mcdp_utils_xml.note_errors_inline import note_error2, note_warning2

from bs4.element import Comment, Tag


show_debug_message_for_corrected_links = False

def get_id2element(soup, att):
    id2element = {}
    duplicates = set()
    
    # ignore the maths
    ignore = set() 
    for element in soup.select('svg [%s]' % att): # node with ID below SVG
        ignore.add(element[att])
    for element in soup.select('svg[%s]' % att): # svg with ID
        ignore.add(element[att])
    for element in soup.select('[%s^="MathJax"]' % att): # stuff created by MathJax
        ignore.add(element[att])
        
    for element in soup.select('[%s]' % att):
        ID = element[att]
        if ID in ignore:
            continue
        if ID in id2element:
            duplicates.add(ID)
            other = id2element[ID]
            for e0 in [element, other]:
                if not 'errored' in e0.attrs.get('class', ''):
                    add_class(e0, 'errored')
                    w = Tag(name='span', attrs={'class':'duplicated-id'})
                    w.string = 'More than one element with id %r.' % ID
                    e0.insert_after(w)
        id2element[element[att]] = element
        
    if duplicates:
        s = ", ".join(sorted(duplicates))
        msg = '%d duplicated %s found (not errored): %s' % (len(duplicates), att, s) 
        logger.error(msg)
    return id2element, duplicates


def check_if_any_href_is_invalid(soup):
    '''
         Checks if references are invalid and tries to correct them. 
         
        if it is of the form "#frag?query" then query is stripped out
    '''
    logger.debug('check_if_any_href_is_invalid')
    
    errors = []
    math_errors = []
    
    # let's first find all the IDs
    id2element, duplicates = get_id2element(soup, 'id')
    _name2element, _duplicates = get_id2element(soup, 'name')


    for a in soup.select('[href^="#"]'):
        href = a['href']
        if a.has_attr('class') and  "mjx-svg-href" in a['class']:
            msg = 'Invalid math reference (sorry, no details): href = %s .' % href
            logger.warning(msg)
            a.insert_before(Comment('Error: %s' % msg))
            math_errors.append(msg)
            continue 
        assert href.startswith('#')
        ID = href[1:]
        # remove query if it exists
        if '?' in ID:
            ID = ID[:ID.index('?')]

        if not ID in id2element:
            # try to fix it 
            
            # if there is already a prefix, remove it 
            if ':' in href:
                i = href.index(':')
                core = href[i+1:]
            else:
                core = ID
                
#             logger.debug('check_if_any_href_is_invalid: not found %r, core %r' % (ID, core))
            
            possible = ['sec', 'sub', 'subsub', 'fig', 'tab', 'code', 'app', 'appsub',
                        'appsubsub',
                        'def', 'eq', 'rem', 'lem', 'prob', 'prop', 'exa', 'thm' ]
            matches = [] 
            others = []
            for possible_prefix in possible:
                why_not = possible_prefix + ':' + core
                others.append(why_not)
                if why_not in id2element:
                    matches.append(why_not)
            
#             logger.debug('others = %r, matches = %r' % (others, matches))
            
            if len(matches) > 1:
                short = 'Ref. error'
                msg = '%s not found, and multiple matches for heuristics (%s)' % (href, matches)
                note_error2(a, short, msg, ['href-invalid', 'href-invalid-missing'])
                
                
            elif len(matches) == 1:
                
                a['href'] = '#' + matches[0]
                
                if show_debug_message_for_corrected_links:
                    short = 'Ref replaced'
                    msg = '%s not found, but corrected in %s' % (href, matches[0])
                    note_warning2(a, short, msg, ['href-replaced'])
                 
            else:
                short = 'Ref. error'
                msg = 'Not found %r (also tried %s)' % (href, ", ".join(others))
                note_error2(a, short, msg, ['href-invalid', 'href-invalid-missing'])
                errors.append(msg)
                    
        if ID in duplicates:
            msg = 'More than one element matching %r.' % href
            short = 'Ref. error'
            note_error2(a, short, msg, ['href-invalid', 'href-invalid-multiple'])
            errors.append(msg)
            
    return errors, math_errors



def fix_subfig_references(soup):
    """
        Changes references like #fig:x to #subfig:x if it exists.
    """ 

    for a in soup.select('a[href^="#fig:"]'):
        name = a['href'][1:]
        
        alternative = 'sub' + name
#         print('considering if it exists %r' % alternative)
        if list(soup.select('#' +alternative)):
            newref = '#sub' + name
#             logger.debug('changing ref %r to %r' % (a['href'],newref))
            a['href'] = newref
         
