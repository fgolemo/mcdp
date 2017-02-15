# -*- coding: utf-8 -*-
from mcdp_web.renderdoc.xmlutils import bs
from bs4.element import Tag, NavigableString

# 
# <dl>
# 
# <dt>
# [<a name="esik09fixed">1</a>]
# </dt>
# <dd>
# Z&nbsp;&Eacute;sik.
#  Fixed point theory.
#  <em>Handbook of Weighted Automata</em>, 2009.
# [&nbsp;<a href="bibliography_bib.html#esik09fixed">bib</a>&nbsp;| 
# <a href="http://dx.doi.org/10.1007/978-3-642-01492-5">DOI</a>&nbsp;]
# 
# </dd>



def get_bibliography(bibfile):
    data = open(bibfile).read()
    frag = bs(data)
    res = Tag(name='div')
    
    ids = []
    for dt in frag.select('dt'):
        assert dt.name == 'dt'
        name = dt.a.attrs['name']
        name = 'bib:' + name
        ids.append(name)
        dd = dt.findNext('dd')
        assert dd.name == 'dd'
        entry = dd.__copy__()
        entry.name = 'cite'
        entry.attrs['id'] = name
        
        try_to_replace_stuff = False
        if try_to_replace_stuff:
            for x in entry.descendants:
                #print('child', x)
                if isinstance(x, NavigableString):
                    s = x.string.encode('utf-8')
                    s = s.replace('\n', ' ')
                    s = s.replace('[', '')
                    s = s.replace('|', '')
                    s = s.replace(']', '')
                    y = NavigableString(unicode(s, 'utf-8'))
                    x.replace_with(y)
                    #print('string %r' % x.string)
                if isinstance(x, Tag) and x.name == 'a' and x.string == 'bib':
                    x.extract()
        res.append(NavigableString('\n'))
        res.append(entry)
        res.append(NavigableString('\n'))
    print('Found %d bib entries.' % len(ids))
    return res
    
    
if __name__ == '__main__':
    
    b = get_bibliography()
    print b