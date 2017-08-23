from mcdp_utils_xml import add_class

from bs4.element import Tag, NavigableString


def other_abbrevs(soup):
    """
        v, val, value   --> mcdp-value
           pos, poset   --> mcdp-poset
           
        <val>x</val> -> <mcdp-value></mcdp-value>
        <pos>x</pos> -> <mcdp-poset></mcdp-poset>
        
        <s> (strikeout!) -> <span> 
        
        <p>TODO:...</p> -> <div class="todo"><p><span>TODO:</span></p>
    """ 
    
    translate = {
        'v': 'mcdp-value',
        'val': 'mcdp-value',
        'value': 'mcdp-value',
        
        'pos': 'mcdp-poset',
        'poset': 'mcdp-poset',
        's': 'span',
    }
    
    for k, v in translate.items():
        for e in soup.select(k):
            e.name = v

    from mcdp_docs.task_markers import substitute_task_markers
    substitute_task_markers(soup)
    substitute_special_paragraphs(soup)
    
    
def substitute_special_paragraphs(soup):
    prefix2class = {
        'TODO: ': 'todo',
        'TOWRITE: ': 'special-par-towrite',  
        'Task: ': 'special-par-task',
        'Remark: ': 'special-par-remark',  
        'Note: ': 'special-par-note',
        'Symptom: ': 'special-par-symptom',
        'Resolution: ': 'special-par-resolution',
        'Bad:': 'special-par-bad',
        'Better:': 'special-par-better',
        'Warning:': 'special-par-warning',
        'Q:': 'special-par-question',
        'A:': 'special-par-answer',
        "Assigned: ": 'special-par-assigned',
        "Author: ": 'special-par-author',
        "Maintainer: ": 'special-par-maintainer',
        "Point of contact: ": 'special-par-point-of-contact',
        "Slack channel: ": 'special-par-point-of-contact',
        # Reference and See are the same thing
        'See: ': 'special-par-see',
        'Reference: ': 'special-par-see',
        
        'Requires: ': 'special-par-requires',
        'Recommended: ': 'special-par-recommended',
        'See also: ': 'special-par-see-also',
    } 
    
    for prefix, klass in prefix2class.items():
        substitute_special_paragraph(soup, prefix, klass)
        
def substitute_special_paragraph(soup, prefix, klass):
    """ 
        Looks for paragraphs that start with a simple string with the given prefix. 
    
        From:
        
            <p>prefix contents</p>
            
        Creates:
        
            <div class='klass-wrap'><p class='klass'>contents</p></div>
    """
    ps = list(soup.select('p'))
    for p in ps:
        # Get first child
        contents = list(p.contents)
        if not contents:
            continue
        c = contents[0]
        if not isinstance(c, NavigableString):
            continue

        s = c.string
        starts = s.lower().startswith(prefix.lower())
        if not starts: 
            continue

        without = s[len(prefix):]
        ns = NavigableString(without)
        c.replaceWith(ns)
    
        div = Tag(name='div')
        add_class(div, klass + '-wrap')
        add_class(p, klass)
        parent = p.parent
        i = parent.index(p)
        p.extract()
        div.append(p)
        parent.insert(i, div)

