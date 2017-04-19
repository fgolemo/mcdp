from bs4.element import Tag

from contracts import contract
from contracts.utils import indent, check_isinstance


__all__ = ['describe_tag']

@contract(tag=Tag, returns=str)
def describe_tag(tag):
    check_isinstance(tag, Tag)
    def c(tag):
        x = unicode(tag).encode('utf-8')
        return x 
    
    s = "This is the tag:"
    s += '\n\n'
    s += indent(c(tag), 'tag |')
    s +='\n\n' + 'This is the tag in context:' + '\n\n'
    
    sc = ""
    if tag.previousSibling is not None:
        sc += c(tag.previousSibling)
    else:
        sc += '<!-- no prev sibling -->'
    sc += c(tag)
    if tag.nextSibling is not None:
        sc += c(tag.next)
    else:
        sc += '<!-- no next sibling -->' 
        
    s += indent(sc, 'tag in context |')
    return s
    
    