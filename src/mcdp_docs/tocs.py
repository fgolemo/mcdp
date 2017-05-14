# -*- coding: utf-8 -*-

from mcdp.logs import logger
from mcdp_docs.toc_number import render_number, number_styles

from bs4.element import Comment, Tag
from contracts.utils import indent


from mcdp_utils_xml.note_errors_inline import note_error_msg
from mcdp_utils_xml.add_class_and_style import add_class
from mcdp_docs.manual_constants import MCDPManualConstants
from collections import namedtuple
from mcdp_utils_xml.parsing import bs

figure_prefixes = ['fig','tab','subfig','code']
cite_prefixes = ['bib']
div_latex_prefixes = ['exa', 'rem', 'lem', 'def', 'prop', 'prob', 'thm']

def element_has_one_of_prefixes(element, prefixes):
    eid = element.attrs.get('id', 'notpresent')
    return any(eid.startswith(_+':') for _  in prefixes)

class GlobalCounter:
    header_id = 1 
    
    
def fix_header_id(header):
    ID = header.get('id', None)
    prefix = None if (ID is None or not ':' in ID) else ID[:ID.index(':')] 
    
    allowed_prefixes_h = {
        'h1': ['sec', 'app', 'part'],
        'h2': ['sub', 'appsub'],
        'h3': ['subsub', 'appsubsub'],
        'h4': ['par'],
    }
    
    if header.name in allowed_prefixes_h: 
        allowed_prefixes = allowed_prefixes_h[header.name]
        default_prefix = allowed_prefixes[0]
        
        if ID is None: 
            header['id'] = '%s:%s' % (default_prefix, GlobalCounter.header_id)
            GlobalCounter.header_id += 1
        else:
            if prefix is None:
                if ID != 'booktitle': 
                    msg = ('Adding prefix %r to current id %r for %s.' % 
                           (default_prefix, ID, header.name))
                    header.insert_before(Comment('Warning: ' + msg))
                    header['id'] = default_prefix + ':' + ID
            else: 
                if prefix not in allowed_prefixes:
                    msg = ('The prefix %r is not allowed for %s (ID=%r)' % 
                           (prefix, header.name, ID))
                    logger.error(msg)
                    header.insert_after(Comment('Error: ' + msg))
    
def get_things_to_index(soup):
    """
        nothing with attribute "notoc"
         
        h1, h2, h3, h4
        figure  with id= "fig:*" or "tab:*" or "subfig:*" or code
    """
    formatter = None
    for h in soup.findAll(['h1', 'h2', 'h3', 'h4', 'figure', 'div', 'cite']):
        
        if formatter is None:
            formatter = h._formatter_for_name("html")

        if h.has_attr('notoc'):
            continue
        
        if h.name in ['h1', 'h2', 'h3', 'h4']:
            fix_header_id(h)
            h_id = h.attrs['id']
            if h.name == 'h1':
                if h_id.startswith('part:'):
                    depth = 1
                elif h_id.startswith('app:'):
                    depth = 2
                elif h_id.startswith('sec:'):
                    depth = 3
                else:
                    raise ValueError(h)
            elif h.name == 'h2':
                depth = 4
            elif h.name == 'h3':
                depth = 5
            elif h.name == 'h4':
                depth = 6
            elif h.name == 'h5':
                depth = 7
            elif h.name == 'h6':
                depth = 8
            
            name = h.decode_contents(formatter=formatter)
            yield h, depth, name
            
        elif h.name in ['figure']:
            if not element_has_one_of_prefixes(h, figure_prefixes):
                continue
            
            figcaption = h.find('figcaption') # XXX: bug because it gets confused with children
            if figcaption is None:
                name = None
            else:
                name = figcaption.decode_contents(formatter=formatter)
            yield h, 100, name
            
        elif h.name in ['div']:
            if not element_has_one_of_prefixes(h, div_latex_prefixes):
                continue
            label = h.find(class_='latex_env_label')
            if label is None:
                name = None
            else:
                name = label.decode_contents(formatter=formatter)
            yield h, 100, name
        else:
            pass
        

def generate_toc(soup):
    stack = [ Item(None, 0, 'root', 'root', []) ]

    headers_depths = list(get_things_to_index(soup))
    #print('iterating headers')
    for header, depth, using in headers_depths:
        
       
            
        item = Item(header, depth, using, header['id'], [])

#         using =  using[:35]
#         m = 'header %s %s   %-50s    %s  ' % (' '*2*depth,  header.name, header['id'],  using)
#         m = m + ' ' * (120-len(m))
#         print(m)
        
        while(stack[-1].depth >= depth):
            stack.pop()
        stack[-1].items.append(item)
        stack.append(item)
        
 
    root = stack[0]

    print('numbering items')
    number_items2(root)
    print(toc_summary(root)) 

    from mcdp_utils_xml import bs

    print('toc iterating')
    # iterate over chapters (below each h1)
    # XXX: this is parts
    for item in root.items:
        s = item.__str__(root=True)
        stoc = bs(s)
        if stoc.ul is not None: # empty document case
            ul = stoc.ul
            ul.extract() 
            ul['class'] = 'toc chapter_toc'
            # todo: add specific h1
            item.tag.insert_after(ul) # XXX: uses <fragment>
            
    print('toc done iterating')
    return root.__str__(root=True)

def toc_summary(root):
    s = ''
    for item in root.depth_first_descendants(): 

        number = item.tag.attrs.get(LABEL_WHAT_NUMBER, '???')
        m = 'depth %s tag %s id %-30s %-20s %s %s  ' % (item.depth, item.tag.name, item.id[:26], number, ' '*2*item.depth,  item.name,)
        m = m + ' ' * (120-len(m))
        s += '\n' + m
    return s


class Item(object):
    def __init__(self, tag, depth, name, _id, items):
        self.tag = tag
        self.name = name
        self.depth = depth
        self.id = _id
        self.items = items 
        self.number = None

    def __str__(self, root=False):
        s = u''
        if not root:
            s += (u"""<a class="toc_link toc_link-depth-%s number_name" href="#%s"></a>""" % (self.depth, self.id))
#             use_name = self.name 
#             s += (u"""<a class="toc_link" href="#%s">
#                         <span class="toc_number">%s –</span> 
#                         <span class="toc_name">%s</span></a>""" % 
#                         (self.id, self.number, use_name))
        if self.items:
            s += '<ul class="toc_ul-depth-%s">' % self.depth
            for item in self.items:
                sitem = indent(item.__str__(), '  ')
                s += '\n  <li class="toc_li-depth-%s">\n%s\n  </li>' % (self.depth, sitem)
            s += '\n</ul>'
        return s
    
    def depth_first_descendants(self):
        for item in self.items:
            yield item
            for item2 in item.depth_first_descendants():
                yield item2

def number_items2(root):
    counters = set(['part', 'app', 'sec', 'sub', 'subsub', 'appsub', 'appsubsub', 'par']
                    + ['fig', 'tab', 'subfig', 'code']
                    + ['exa', 'rem', 'lem', 'def', 'prop', 'prob', 'thm'])
    
    resets = {
        'part': [],
        'sec': ['sub', 'subsub', 'par'],
        'sub': ['subsub', 'par'],
        'subsub': ['par'],
        'app': ['appsub', 'appsubsub', 'par'],
        'appsub': ['appsubsub', 'par'],
        'appsubsub': ['par'],
        'par': [],
        'fig': ['subfig'],
        'subfig': [],
        'tab': [],
        'code': [],
        'exa': [],
        'rem': [],
        'lem': [],
        'def': [],
        'prop': [],
        'prob': [],
        'thm': [],
    }
    Label = namedtuple('Label', 'what number label_self')
    labels = {
        'part': Label('Part', '${part}', ''),
        'sec': Label('Chapter', '${sec}', ''),
        'sub': Label('Section', '${sec}.${sub}', ''),
        'subsub': Label('Subsection', '${sec}.${sub}.${subsub}', '${subsub}) '),
        'par': Label('Paragraph', '${par|lower-alpha}', ''),
        'app': Label('Appendix', '${app|upper-alpha}', ''),
        'appsub': Label('Section', '${app|upper-alpha}.${appsub}', ''),
        'appsubsub': Label('Subsection', '${app|upper-alpha}.${appsub}.${appsubsub}', ''),
        # global counters 
        'fig': Label('Figure', '${fig}', ''),
        'subfig': Label('Figure', '${fig}${subfig|lower-alpha}', '(${subfig|lower-alpha})'),
        'tab': Label('Table', '${tab}', ''),
        'code': Label('Listing', '${code}', ''),
        'rem': Label('Remark', '${rem}', ''),
        'lem': Label('Lemma', '${lem}', ''),
        'def': Label('Definition', '${def}', ''),
        'prob': Label('Problem', '${prob}', ''),
        'prop': Label('Proposition', '${prop}', ''),
        'thm': Label('Theorem', '${thm}', ''),
        'exa': Label('Example', '${exa}', ''),
         
    }
    
    for c in counters:
        assert c in resets,c
        assert c in labels,c  
    from collections import defaultdict
    counter_parents = defaultdict(lambda: set())
    for c, cc in resets.items():
        for x in cc: 
            counter_parents[x].add(c)

    counter_state = {}
    for counter in counters:
        counter_state[counter] = 0       
        
    for item in root.depth_first_descendants():
        counter = item.id.split(":")[0]
#         print('counter %s id %s %s' % (counter, item.id, counter_state))
        if counter in counters:
            counter_state[counter] += 1
            for counter_to_reset in resets[counter]:
                counter_state[counter_to_reset] = 0
            
            label_spec = labels[counter]
            what = label_spec.what
            number = render(label_spec.number, counter_state)
            
            item.tag.attrs[LABEL_NAME] = item.name
            item.tag.attrs[LABEL_WHAT] = what
            item.tag.attrs[LABEL_SELF] = render(label_spec.label_self, counter_state)
            
            if item.name is None:
                item.tag.attrs[LABEL_WHAT_NUMBER_NAME] = what + ' ' + number 
            else:
                item.tag.attrs[LABEL_WHAT_NUMBER_NAME] = what + ' ' + number + ' - ' + item.name
            item.tag.attrs[LABEL_WHAT_NUMBER] = what + ' ' + number
            item.tag.attrs[LABEL_NUMBER] = number
            
            allattrs = [LABEL_NAME, LABEL_WHAT, LABEL_WHAT_NUMBER_NAME, LABEL_NUMBER, LABEL_SELF]
            for c in counters:
                if c in counter_parents[counter] or c == counter:
                    attname = 'counter-%s' % c
                    allattrs.append(attname)
                    item.tag.attrs[attname] = counter_state[c]

            if item.tag.name == 'figure':
                # also copy to the caption
                for figcaption in item.tag.findAll(['figcaption']):
                    if figcaption.parent != item.tag:
                        continue
                    for x in allattrs:
                        figcaption.attrs[x] = item.tag.attrs[x]
                        
LABEL_NAME = 'label-name'
LABEL_NUMBER = 'label-number'
LABEL_WHAT = 'label-what'
LABEL_SELF = 'label-self'
LABEL_WHAT_NUMBER_NAME = 'label-what-number-name'
LABEL_WHAT_NUMBER = 'label-what-number'

def render(s, counter_state):
    reps = {}
    for c, v in counter_state.items():
        for style in number_styles:
            reps['${%s|%s}' % (c, style)] = render_number(v, style)
        reps['${%s}' % c] = render_number(v, 'decimal')
        
    for k, v in reps.items():
        s = s.replace(k, v)
    return s

def substituting_empty_links(soup, raise_errors=False):
    logger.debug('substituting_empty_links')
    n = 0
    nerrors = 0
    for a, element_id, element in get_links_to_fragment(soup):
        empty = len(list(a.descendants)) == 0
        if not empty: continue
#             logger.debug('%s %s %s %s' % (a, element_id, element, empty))
        # a is empty
        n += 1
        if element:
            if (not LABEL_WHAT_NUMBER  in element.attrs) or \
                (not LABEL_NAME  in element.attrs):
                msg = 'Could not find attributes %s or %s in %s' % (LABEL_NAME, LABEL_WHAT_NUMBER, element)
                note_error_msg(a, msg)
                nerrors += 1
                if raise_errors:
                    raise ValueError(msg)
            else:
                label_what_number = element.attrs[LABEL_WHAT_NUMBER]
                label_number = element.attrs[LABEL_NUMBER]
                label_what = element.attrs[LABEL_WHAT]
                label_name = element.attrs[LABEL_NAME]
                classes = a.attrs.get('class', [])
                if 'toc_link' in classes:
                    
                    s = Tag(name='span')
                    s.string = label_what
                    add_class(s, 'toc_what')
                    a.append(s)
                    
                    a.append(' ')
                    
                    s = Tag(name='span')
                    s.string = label_number
                    add_class(s, 'toc_number')
                    a.append(s)

                    s = Tag(name='span')
                    s.string = ' - '
                    add_class(s, 'toc_sep')
                    a.append(s)
                    
                    if '<' in label_name:
                        contents = bs(label_name)
                        a.append(contents)
                    else:
                        s = Tag(name='span')
                        if label_name is None:
                            s.string = '(unnamed)' # XXX
                        else:
                            
                            s.string = label_name
                        add_class(s, 'toc_name')
                        a.append(s)
                    
                    
                else:
                    if MCDPManualConstants.CLASS_ONLY_NUMBER in classes:
                        label = label_number
                    elif MCDPManualConstants.CLASS_NUMBER_NAME in classes:
                        if label_name is None:
                            label = label_what_number + ' - ' + '(unnamed)' # warning
                        else:
                            label = label_what_number + ' - ' + label_name
                    elif MCDPManualConstants.CLASS_ONLY_NAME in classes:
                        if label_name is None:
                            label =  '(unnamed)' # warning
                        else:
                            label = label_name
                    else:
                        label = label_what_number
                    
                    span1 = Tag(name='span')
                    add_class(span1, 'reflabel')
                    span1.string = label
                    a.append(span1)

                
        else:
            msg = ('Cannot find %s' % element_id)
            note_error_msg(a, msg)
            nerrors += 1
            if raise_errors:
                raise ValueError(msg)
    logger.debug('substituting_empty_links: %d total, %d errors' % (n, nerrors))
    
    
def get_links_to_fragment(soup):
    """
        Find all links that have a reference to a fragment.
    """
#     
# s.findAll(lambda tag: tag.name == 'p' and tag.find(True) is None and 
# (tag.string is None or tag.string.strip()=="")) 
    for element in soup.find_all('a'):
        if not 'href' in element.attrs:
            continue
        href = element.attrs['href']
        if href.startswith('#'):
            eid = href[1:]
            linked = soup.find(id=eid)
            yield element, eid, linked

