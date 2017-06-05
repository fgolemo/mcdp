# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_report.html import get_css_filename
from mcdp_utils_xml import bs,\
    check_html_fragment, to_html_stripping_fragment_document

from bs4.element import NavigableString, Tag


@contract(body_contents=str, returns=str)
def get_minimal_document(body_contents, title=None,
                         add_markdown_css=False, add_manual_css=False, stylesheet=None, extra_css=None):
    """ Creates the minimal html document with MCDPL css.
    
        add_markdown_css: language + markdown
        add_manual_css: language + markdown + (manual*)
    
        extra_css = additional CSS contents
     """
    check_html_fragment(body_contents)
    soup = bs("")
    assert soup.name == 'fragment'
    
    if title is None:
        title = ''
        
    html = Tag(name='html')
    
    head = Tag(name='head')
    body = Tag(name='body') 
    
    head.append(Tag(name='meta', attrs={'http-equiv':"Content-Type",
                                        'content': "application/xhtml+xml; charset=utf-8"}))
    
    if stylesheet is None:
        stylesheet = 'v_mcdp_render_default'
        
    if add_markdown_css or add_manual_css:
        link = Tag(name='link')
        link['rel'] = 'stylesheet'
        link['type'] = 'text/css'
        link['href'] = get_css_filename('compiled/%s' % stylesheet)
        head.append(link) 
        

    tag_title = Tag(name='title')
    tag_title.append(NavigableString(title))
    head.append(tag_title) 
    parsed = bs(body_contents)
     
    assert parsed.name == 'fragment'
    parsed.name = 'div'
    body.append(parsed)
    html.append(head)
    html.append(body)
    soup.append(html)
    
    if extra_css is not None:
        add_extra_css(soup, extra_css)
        
    s = to_html_stripping_fragment_document(soup)
    assert not 'DOCTYPE' in s
#     s = html.prettify() # no: it removes empty text nodes

#     ns="""<?xml version="1.0" encoding="utf-8" ?>"""
    ns="""<!DOCTYPE html PUBLIC
    "-//W3C//DTD XHTML 1.1 plus MathML 2.0 plus SVG 1.1//EN"
    "http://www.w3.org/2002/04/xhtml-math-svg/xhtml-math-svg.dtd">"""
    res = ns + '\n' +  s
    
#     if add_manual_css and MCDPConstants.manual_link_css_instead_of_including:
#         assert 'manual.css' in res, res
    
    res = res.replace('<div><!DOCTYPE html>', '<div>')
        
    return res

def add_extra_css(soup, css):
    head = soup.find('head')
    if head is None:
        msg = 'Could not find head element.'
        raise Exception(msg)
    
    style = Tag(name='style', attrs={'type':'text/css'})
    style.string = css
    head.append(style)
    