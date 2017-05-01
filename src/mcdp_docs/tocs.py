# -*- coding: utf-8 -*-

from mcdp.logs import logger

from bs4.element import Tag, Comment

def generate_toc(soup):
    header_id = 1 

    stack = [ Item(None, 0, 'root', 'root', []) ]

    headers = list(soup.findAll(['h1', 'h2', 'h3', 'h4']))
    #print('iterating headers')
    formatter="html"
    formatter = headers[0]._formatter_for_name(formatter)
    for header in headers:
        if header.has_attr('notoc'):
            continue
        ID = header.get('id', None)
        prefix = None if (ID is None or not ':' in ID) else ID[:ID.index(':')] 
        
        allowed_prefixes = {
            'h1': ['sec', 'app', 'part'],
            'h2': ['sub', 'appsub'],
            'h3': ['subsub', 'appsubsub'],
            'h4': ['par'],
        }[header.name]
        default_prefix = allowed_prefixes[0]
        
        if ID is None: 
            header['id'] = '%s:%s' % (default_prefix, header_id)
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
                    
        depth = int(header.name[1])

        using = header.decode_contents(formatter=formatter)
        item = Item(header, depth, using, header['id'], [])

        using =  using[:35]
        m = 'header %s %s   %-50s    %s  ' % (' '*2*depth,  header.name, header['id'],  using)
        m = m + ' ' * (120-len(m))
        print(m)
        
        while(stack[-1].depth >= depth):
            stack.pop()
        stack[-1].items.append(item)
        stack.append(item)
        header_id += 1
 
    root = stack[0]

    print('numbering items')
    root.number_items(prefix='', level=0)

    from mcdp_utils_xml import bs

    print('toc iterating')
    # iterate over chapters (below each h1)
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


class Item(object):
    def __init__(self, tag, depth, name, _id, items):
        self.tag = tag
        self.name = name
        self.depth = depth
        self.id = _id
        self.items = items
#             for i in items:
#                 assert isinstance(items)

        self.number = None

    def number_items(self, prefix, level):
        self.number = prefix

        if self.tag is not None:
            # add a span inside the header
            
            if False:
                span = Tag(name='span')
                span['class'] = 'toc_number'
                span.string = prefix + ' – '
                self.tag.insert(0, span)
            else:
                msg = 'number_items: By my count, this should be %r.' % prefix
                self.tag.insert_after(Comment(msg))
            #self.tag.string = prefix + ' - ' + self.tag.string

        def get_number(i, level):
            if level == 0 or level == 1:
                headings = ['%d' % (j + 1) for j in range(20)]
            elif level == 2:
                headings = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                    'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'Z']

            else:
                return ''

            if i >= len(headings):
                msg = 'i = %d level %s headings = %s' % (i, level, headings)
                #logger.error(msg)
                return 'extraheading%s' % i
                #raise ValueError(msg)
            return headings[i]

        if prefix:
            prefix = prefix + '.'
        for i, item in enumerate(self.items):
            item_prefix = prefix + get_number(i, level)
            item.number_items(item_prefix, level + 1)

    def __str__(self, root=False):
        s = u''
        if not root:
            use_name = self.name
#                 if '<'in self.name:
#                     print 'name: (%s)' % self.name
#                     use_name = 'name of link'
#                 
            s += (u"""<a class="toc_link" href="#%s">
                        <span class="toc_number">%s –</span> 
                        <span class="toc_name">%s</span></a>""" % 
                        (self.id, self.number, use_name))
        if self.items:
            s += '<ul>'
            for item in self.items:
                s += '<li>%s</li>' % item
            s += '</ul>'
        return s
