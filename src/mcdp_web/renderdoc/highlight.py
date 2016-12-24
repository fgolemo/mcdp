# -*- coding: utf-8 -*-
import base64
import hashlib
import os
import shutil
import sys
from tempfile import mkdtemp
import traceback

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, indent
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parse_interface import (parse_template_refine, parse_poset_refine,
                                       parse_ndp_refine)
from mcdp_lang.suggestions import get_suggestions, apply_suggestions
from mcdp_lang.syntax import Syntax
from mcdp_library import MCDPLibrary
from mcdp_report.generic_report_utils import (
    NotPlottable, enlarge, get_plotters)
from mcdp_report.html import ast_to_html, get_markdown_css
from mcdp_report.plotters.get_plotters_imp import get_all_available_plotters
from mcdp_web.images.images import (get_mime_for_format)
from mcdp_web.renderdoc.xmlutils import bs, to_html_stripping_fragment,\
    check_html_fragment, to_html_stripping_fragment_document, describe_tag
from mocdp import ATTR_LOAD_NAME, logger, get_mcdp_tmp_dir, MCDPConstants
from mocdp.comp.context import Context
from mocdp.exceptions import DPSemanticError, DPSyntaxError, DPInternalError
from reprep import Report
from system_cmd import CmdException, system_cmd_result


from mcdp_figures import( MakeFiguresNDP, MakeFiguresTemplate, 
    MakeFiguresPoset)
import textwrap

import bs4




@contract(returns=str, html=str)
def html_interpret(library, html, raise_errors=False, 
                   generate_pdf=False, realpath='unavailable'):
    # clone library, so that we don't pollute it 
    # with our private definitions
    library = library.clone()
    load_fragments(library, html, realpath=realpath)

    html = highlight_mcdp_code(library, html,
                               generate_pdf=generate_pdf,
                               raise_errors=raise_errors,
                               realpath=realpath)

    html = make_plots(library, html,
                      raise_errors=raise_errors,
                      realpath=realpath)
    # let's do make_plots first; then make_figures will 
    # check for remaining <render> elements.
    html = make_figures(library, html,
                        generate_pdf=generate_pdf,
                        raise_error_dp=raise_errors,
                        raise_error_others=raise_errors,
                        realpath=realpath)


#     if False:
#         html = add_br_before_pres(html)
#     print 'after make_plots: %s' % html

    return html

def make_image_tag_from_png(f):
    def ff(*args, **kwargs):
        png = f(*args, **kwargs)
        rendered = create_img_png_base64( png)
        return rendered
    return ff

def make_pre(f):
    def ff(*args, **kwargs):
        res = f(*args, **kwargs)
        pre = Tag(name='pre')  #  **{'class': 'print_value'})
        code = Tag(name='code')
        code.string = res
        pre.append(code)
        return pre
    return ff

    
def load_or_parse_from_tag(tag, load, parse):
    """ 
        If tag.string is not None, then it parses the contents
        using the function parse.
        
        Otherwise it tries to load the id given.
        
        If empty and no ID, raises excxception.
        
        Either 
            <tag  class=... id='poset'>
        or 
            <tag  class=...>my code </tag
    """
    if tag.string is None: # or not tag.string.strip():
        if not tag.has_attr('id'):
            msg = "If <img> is empty then it needs to have an id."
            raise_desc(ValueError, msg, tag=str(tag))
        # load it
        tag_id = tag['id'].encode('utf-8')
        vu = load(tag_id)
    else:
        source_code = get_source_code(tag)
        vu = parse(source_code)    
    return vu

@contract(frag=str, returns=str)
def make_plots(library, frag, raise_errors, realpath):
    """
        Looks for things like:
        
         
        <img class="value_plot_generic">VALUE</img>
        <img class="value_plot_generic" id='value"/>
        
        <pre class="print_value" id='value"/>
        <pre class="print_value">VALUE</img>
    
    """
    soup = bs(frag)

    def go(selector, plotter, load, parse):
        for tag in soup.select(selector):

            try:
                # load value with units in vu
                
                def parsing(source_code):
                    context = Context()
                    return parse(source_code, realpath=realpath, context=context)
                    
                vu = load_or_parse_from_tag(tag, load, parsing) 
                
                rendered = plotter(tag, vu)

                if tag.has_attr('style'):
                    style = tag['style']
                else:
                    style = ''

                if style:
                    rendered['style'] = style
                tag.replaceWith(rendered)

            except (DPSyntaxError, DPSemanticError) as e:
                if raise_errors:
                    raise
                logger.error(str(e))  # XXX
                t = Tag(name='pre', **{'class': 'error %s' % type(e).__name__})
                t.string = str(e)
                tag.insert_after(t)
            except Exception as e:
                if raise_errors:
                    raise
                t = Tag(name='pre', **{'class': 'error %s' % type(e).__name__})
                t.string = traceback.format_exc(e)
                tag.insert_after(t)
    
    @make_image_tag_from_png
    def plot_value_generic(tag, vu):  # @UnusedVariable
        r = Report()
        f = r.figure()
        try:
            available = dict(get_plotters(get_all_available_plotters(), vu.unit))
            assert available
        except NotPlottable as e:
            msg = 'No plotters available for %s' % vu.unit
            raise_wrapped(ValueError, e, msg, compact=True)

        plotter = list(available.values())[0]

        axis = plotter.axis_for_sequence(vu.unit, [vu.value])
        axis = enlarge(axis, 0.15)
        with f.plot('generic') as pylab:
            plotter.plot(pylab, axis, vu.unit, vu.value, params={})
            pylab.axis(axis)
        png_node = r.resolve_url('png')
        png = png_node.get_raw_data()
        return png
    
    @make_pre
    def print_value(tag, vu):  # @UnusedVariable
        s = vu.unit.format(vu.value)
        return s
    
    @make_pre
    def print_mcdp(tag, ndp):  # @UnusedVariable
        return ndp.__str__()
    
    # parse(string, realpath)
    const = dict(load=library.load_constant, parse=library.parse_constant)
    mcdp = dict(load=library.load_ndp, parse=library.parse_ndp)
    go("img.plot_value_generic", plot_value_generic, **const)
    go("render.plot_value_generic", plot_value_generic, **const)
    go("pre.print_value", print_value, **const)
    go("pre.print_mcdp", print_mcdp, **mcdp)
    return to_html_stripping_fragment(soup)

def load_fragments(library, frag, realpath):
    """
        loads all the codes specified as
         
            <pre class="mcdp" id='...'>...</pre> 
            <pre class="mcdp_poset" id='...'>...</pre>
            <pre class="mcdp_template" id='...'>...</pre>
        
    """
    soup = bs(frag)

    for tag in soup.select('pre.mcdp'):
        if tag.string is None or not tag.string.strip():
            continue

        if tag.has_attr('id'):
            id_ndp = tag['id'].encode('utf-8')
            source_code = get_source_code(tag)

            basename = '%s.%s' % (id_ndp, MCDPLibrary.ext_ndps)
            res = dict(data=source_code, realpath=realpath)

            if basename in library.file_to_contents:
                msg = 'The id %r has already been used previously.' % basename
                raise_desc(ValueError, msg, tag=str(tag),
                           known=library.file_to_contents[basename])

            library.file_to_contents[basename] = res

    for tag in soup.select('pre.mcdp_poset'):
        if tag.string is None:# or not tag.string.strip():
            continue

        if tag.has_attr('id'):
            id_ndp = tag['id'].encode('utf-8')
            source_code = get_source_code(tag)

            basename = '%s.%s' % (id_ndp, MCDPLibrary.ext_posets)
            res = dict(data=source_code, realpath=realpath)

            if basename in library.file_to_contents:
                msg = 'Duplicated entry.'
                raise_desc(ValueError, msg, tag=str(tag),
                           known=library.file_to_contents[basename])

            library.file_to_contents[basename] = res

    for tag in soup.select('pre.mcdp_template'):
        if tag.string is None:# or not tag.string.strip():
            continue

        if tag.has_attr('id'):
            id_ndp = tag['id'].encode('utf-8')
            source_code = get_source_code(tag)

            basename = '%s.%s' % (id_ndp, MCDPLibrary.ext_templates)
            res = dict(data=source_code, realpath=realpath)

            if basename in library.file_to_contents:
                msg = 'Duplicated entry.'
                raise_desc(ValueError, msg, tag=str(tag),
                           known=library.file_to_contents[basename])

            library.file_to_contents[basename] = res
            
            
def escape_for_mathjax(html):
    """ Escapes dollars in code 
     
    """
    soup = bs(html)
    for code in soup.select('code, mcdp-poset, mcdp-value, mcdp-fvalue, mcdp-rvalue, render'):
        if not code.string:
            continue
        #unicode
        s = code.string
        if '$' in code.string:
            s = s.replace('$', 'DOLLAR')
            
        code.string = s
    
    res = to_html_stripping_fragment(soup) 
    return res

    
def escape_ticks_before_markdown(html):
    """ Escapes backticks and quotes in code 
    
        Also removes comments <!--- -->
    """
    soup = bs(html)
    for code in soup.select('code, pre, mcdp-poset, mcdp-value, mcdp-fvalue, mcdp-rvalue, render'):
        if not code.string:
            continue
        #unicode
        s = code.string
        if '`' in code.string:
            s = s.replace('`', '&#96;')
#             print('replacing %r -> %r' %(code.string, s))
            
        if '"' in code.string:
            s = s.replace('"', '&quot;')
#             print('replacing %r -> %r' %(code.string, s))
            
        code.string = s
    
    comments=soup.find_all(string=lambda text:isinstance(text, bs4.Comment))
    for c in comments:
#         print('stripping comment %s' % str(c))
        c.extract()
    
    res = to_html_stripping_fragment(soup)
     
    return res

def fix_subfig_references(html):
    """
        Changes references like #fig:x to #subfig:x if it exists.
    """
    soup = bs(html) 

    for a in soup.select('a[href^="#fig:"]'):
        name = a['href'][1:]
        
        alternative = 'sub' + name
#         print('considering if it exists %r' % alternative)
        if list(soup.select('#' +alternative)):
            newref = '#sub' + name
            logger.debug('changing ref %r to %r' % (a['href'],newref))
            a['href'] = newref
        
    res = to_html_stripping_fragment(soup)
    return res

def make_figure_from_figureid_attr(html):
    """
        Makes a figure:
            <e figure-id='fig:ure' figure-caption='ciao'/> 
                    
        <figure id="fig:ure">
            <e figure-id='fig:ure' figure-caption='ciao'/>
            <figcaption>ciao</figcaption>
        </figure>

        Makes a table:
            <e figure-id='tab:ure' figure-caption='ciao'/>
            
        becomes
        
        
        
        
    """
    soup = bs(html) 
    
    for towrap in soup.select('[figure-id]'):
        ID = towrap['figure-id']
        parent = towrap.parent
        fig = Tag(name='figure')
        fig['id'] = ID
        caption_below = True
        if ID.startswith('fig:'):
            add_class(fig, 'figure')
        elif ID.startswith('subfig:'):
            add_class(fig, 'subfloat')
        elif ID.startswith('tab:'):
            add_class(fig, 'table')
            caption_below = False
        elif ID.startswith('code:'):
            add_class(fig, 'code')
            pass
        else:
            msg = 'The ID %r should start with fig: or tab: or code:' % ID
            raise_desc(ValueError, msg, tag=describe_tag(towrap))
            
        if towrap.has_attr('figure-caption'):
            caption = towrap['figure-caption']
        else:
            caption = ''
        figcaption = Tag(name='figcaption')
        figcaption.append(NavigableString(caption))
        i = parent.index(towrap)
        towrap.extract()
        fig.append(towrap)
        
        if caption_below:
            fig.append(figcaption)
        else:
            fig.insert(0, figcaption)
        
        parent.insert(i, fig)
        
    res = to_html_stripping_fragment(soup)
    return res

def mark_console_pres(html):
    soup = bs(html)
    #     print indent(html, 'mark_console_pres ')
    
    for code in soup.select('pre code'):
        pre = code.parent
        if code.string is None:
            continue
        s0 = code.string
        
        from HTMLParser import HTMLParser
        h = HTMLParser()
        s = h.unescape(s0)
        if s != s0:
#             print('decoded %r -> %r' % (s0, s))
            pass  
        
        beg = s.strip()
        if beg.startswith('DOLLAR') or beg.startswith('$'):
            pass
#             print('it is console (%r)' % s)
        else:
#             print('not console (%r)' % s)
            continue

        add_class(pre, 'console')

        code.string = ''
        
        lines = s.split('\n')
        
        programs = ['sudo', 'pip', 'git', 'python', 'cd', 'apt-get',
                    'mcdp-web', 'mcdp-solve', 'mcdp-render',
                    'mcdp-plot','mcdp-eval','mcdp-render-manual']
        program_commands = ['install', 'develop', 'clone']
        
        def is_program(x, l):
            if x == 'git' and 'apt-get' in l:
                return False
            return x in programs
            
        for j, line in enumerate(lines):
            tokens = line.split(' ')
            for i, token in enumerate(tokens):
                if token in  ['$', 'DOLLAR']:
                    # add <span class=console_sign>$</span>
                    e = Tag(name='span')
                    e['class'] = 'console_sign'
                    e.string = '$'
                    code.append(e)
                elif is_program(token, line):
                    e = Tag(name='span')
                    e['class'] = '%s program' % token
                    e.string = token
                    code.append(e)
                elif token in program_commands:
                    e = Tag(name='span')
                    e['class'] = '%s program_command' % token
                    e.string = token
                    code.append(e)
                elif token and token[0] == '-':
                    e = Tag(name='span')
                    e['class'] = 'program_option'
                    e.string = token
                    code.append(e)
                else:
                    code.append(NavigableString(token))
                    
                is_last = i == len(tokens) - 1
                if not is_last:
                    code.append(NavigableString(' '))
            
            is_last_line = j == len(lines) - 1
            if not is_last_line:
                code.append(NavigableString('\n'))

        
    res = to_html_stripping_fragment(soup) 
    return res

def get_source_code(tag):
    """ Gets the string attribute. 
    
        encodes as utf-8
        removes initial whitespace newlines
        converts tabs to spaces
        
        decodes entities
    """
    if tag.string is None:
        raise ValueError(str(tag))

    s0 = tag.string

    from HTMLParser import HTMLParser
    h = HTMLParser()
    s1 = h.unescape(s0)
#     if False:
#         if s1 != s0:
# #             print('decoded %r -> %r' % (s0, s1))
#             pass

    source_code = s1.encode('utf-8')

    # remove first newline
    while source_code and source_code[0] == '\n':
        source_code = source_code[1:]

#     print(indent(source_code, 'bef|'))
    # remove common whitespace (so that we can indent html elements)
    source_code = textwrap.dedent(source_code)
#     print(indent(source_code, 'aft|'))
    #source_code = source_code.replace('\t', ' ' * 4)
    

    return source_code


@contract(body_contents=str, returns=str)
def get_minimal_document(body_contents, title=None,
                         add_markdown_css=False, add_manual_css=False):
    """ Creates the minimal html document with MCDPL css.
    
        add_markdown_css: language + markdown
        add_manual_css: language + markdown + (manual*)
    
     """
    check_html_fragment(body_contents)
    soup = bs("")
    assert soup.name == 'fragment'
    
    if title is None:
        title = ''
        
    html = Tag(name='html')
    
    head = Tag(name='head')
    body = Tag(name='body')
    css = Tag(name='style', attrs=dict(type='text/css'))
    # <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
#     if False:
#         meta = new_tag('meta')
#         meta['http-equiv'] = "Content-Type"
#         ctype = 'application/xhtml+xml' 
#         meta['content'] = "%s; charset=utf-8" % ctype
#         head.append(meta)
#     if True:
    head.append(Tag(name='meta', attrs=dict(charset='UTF-8')))
    
    tag_title = Tag(name='title')
    tag_title.append(NavigableString(title))
    head.append(tag_title)

    if add_markdown_css and not add_manual_css:
        from mcdp_report.html import get_language_css
        mcdp_css = get_language_css()
        markdown_css = get_markdown_css()
        allcss = mcdp_css + '\n' + markdown_css
        css.append(NavigableString(allcss))
        head.append(css)
    
    if add_manual_css:
        from mcdp_docs.manual_join_imp import get_manual_css_frag
        frags = indent(get_manual_css_frag(), ' '*10)
        frag = bs(frags)

        children = list(frag.children)
        for element in children:
            head.append(element)
    
    parsed = bs(body_contents)
    
#     assert parsed.html is not None
#     assert parsed.html.body is not None
    assert parsed.name == 'fragment'
    parsed.name = 'div'
    body.append(parsed)
    html.append(head)
    html.append(body)
    soup.append(html)
    s = to_html_stripping_fragment_document(soup)
    assert not 'DOCTYPE' in s
#     s = html.prettify() # not it removes empty text nodes

#     ns="""<?xml version="1.0" encoding="utf-8" ?>"""
    ns="""<!DOCTYPE html PUBLIC
    "-//W3C//DTD XHTML 1.1 plus MathML 2.0 plus SVG 1.1//EN"
    "http://www.w3.org/2002/04/xhtml-math-svg/xhtml-math-svg.dtd">"""
    res = ns + '\n' +  s
    
    if add_manual_css and MCDPConstants.manual_link_css_instead_of_including:
        assert 'manual.css' in res, res
    
    res = res.replace('<div><!DOCTYPE html>', '<div>')
        
    return res


def get_ast_as_pdf(s, parse_expr):
    s = s.replace('\t', '    ')
    contents = ast_to_html(s,
                       ignore_line=None, parse_expr=parse_expr,
                       add_line_gutter=False)
    html = get_minimal_document(contents)
    
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    prefix = 'get_ast_as_pdf()'
    d = mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
    
    try:
        f_html = os.path.join(d, 'file.html')
        with open(f_html, 'w') as f:
            f.write(html)
            
        try:
            f_pdf = os.path.join(d, 'file.pdf')
            cmd= ['wkhtmltopdf','-s','A1',f_html,f_pdf]
            system_cmd_result(
                    d, cmd, 
                    display_stdout=False,
                    display_stderr=False,
                    raise_on_error=True)
    
            with open(f_pdf) as f:
                data = f.read()
            
            data = crop_pdf(data, margins=0)
    
            return data
        except CmdException as e:
            raise e
    finally:
        shutil.rmtree(d)


def crop_pdf(pdf, margins=0):
    
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    prefix = 'crop_pdf()'
    d = mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
    
    try:
        f_pdf = os.path.join(d, 'file.pdf')
        with open(f_pdf, 'w') as f:
            f.write(pdf)
        f_pdf_crop = os.path.join(d, 'file_crop.pdf')
        cmd = [
            'pdfcrop', 
            '--margins', 
            str(margins), 
            f_pdf, 
            f_pdf_crop,
        ]
        system_cmd_result(
                d, cmd,
                display_stdout=False,
                display_stderr=False,
                raise_on_error=True)
    
        with open(f_pdf_crop) as f:
            data = f.read()
        return data
    finally:
        shutil.rmtree(d)
        
def highlight_mcdp_code(library, frag, realpath, generate_pdf=False, raise_errors=False):
#     print(indent(frag, 'highlight_mcdp_code '))
    """ Looks for codes like:
    
    <pre class="mcdp">mcdp {
        # empty model
    }
    </pre>
    
        and does syntax hihglighting.
    """

    soup = bs(frag)
    assert soup.name == 'fragment'

    def go(selector, parse_expr, extension, use_pre=True, refine=None):
        for tag in soup.select(selector):
            try:
                if tag.string is None: # or not tag.string.strip():
                    if not tag.has_attr('id'):
                        msg = "If <pre> is empty then it needs to have an id."
                        raise_desc(ValueError, msg, tag=describe_tag(tag))
                        
                    # load it
                    tag_id = tag['id'].encode('utf-8')
                    basename = '%s.%s' % (tag_id, extension)
                    data = library._get_file_data(basename)
                    source_code = data['data']
                else:
                    source_code = get_source_code(tag)
                    
                # prettify. 
                # remove spurious indentation
                source_code = source_code.strip()
                
                do_apply_suggestions = (not tag.has_attr('noprettify') and
                                        not tag.has_attr('np'))
                # then apply suggestions
                try:
                    if do_apply_suggestions:
                        x = parse_wrap(parse_expr, source_code)[0]
                        xr = parse_ndp_refine(x, Context())
                        suggestions = get_suggestions(xr)
                        source_code = apply_suggestions(source_code, suggestions)
                except DPSyntaxError:
                    msg = 'Error while parsing this tag:\n\n'
                    msg += indent(str(tag), '   ')
                    
                    msg += '\n\n' + 'source code:' + '\n\n'
                    msg += indent(source_code, '   ')
                    logger.error(msg)
                    raise
                # we don't want the browser to choose different tab size
                #source_code = source_code.replace('\t', ' ' * 4)   
    
                # we are not using it
                _realpath = realpath
                context = Context()
                def postprocess(x):
                    if refine is not None:
                        return refine(x, context=context)
                    else:
                        return x
#                 print('rendering source code %r' % source_code)
                html = ast_to_html(source_code, parse_expr=parse_expr,
                                                add_line_gutter=False,
                                                postprocess=postprocess)
                
                for w in context.warnings:
                    if w.where is not None:
                        from mcdp_web.editor_fancy.app_editor_fancy_generic import html_mark
                        html = html_mark(html, w.where, "language_warning")
                        
                frag2 = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
                
#                 texts = [i for i in frag2.recursiveChildGenerator() 
#                         if type(i) == NavigableString]
#                 for t in texts:
#                     s = t.string
#                     if ' ' in s:
# 
#                         s = s.replace(' ', ' ')
#                         r = Tag(name='span', attrs={'class': 'space_in_code'})
#                         r.append(NavigableString(s))
#                         t.replace_with(r)
                    
                if use_pre:
                    rendered = frag2.pre
                    if not rendered.has_attr('class'):
                        rendered['class'] = ""
                    if tag.has_attr('label'):
                        text = tag['label']
                        tag_label = Tag(name='span')
                        add_class(tag_label, 'label')
                        add_class(tag_label, 'label_inside')
                        tag_label.append(NavigableString(text))
                        
                        rendered.insert(0, tag_label)
                        
                        tag_label_outside = Tag(name='span')
                        add_class(tag_label_outside, 'label')
                        add_class(tag_label_outside, 'label_outside')
                        tag_label_outside.append(NavigableString(text))
                        tag.insert_before(tag_label_outside)
                        
                    max_len = max_len_of_pre_html(html)
                    frag2.pre['string_len'] = max_len
                    
                    if tag.has_attr('label'): 
                        add_class(rendered, 'has_label')
                        max_len = max(max_len, len(tag['label']) + 6)
                        
#                     add_style_for_size(frag2.pre, max_len)
                    style = ''
                else:
                    # using <code>
                    rendered = frag2.pre.code
                    if not rendered.has_attr('class'):
                        rendered['class'] = ""

                    style = ''

                if tag.has_attr('style'):
                    style = style + tag['style'] 
                    
                if style:
                    rendered['style'] = style

                if tag.has_attr('class'):
                    add_class(rendered, tag['class'])

                if tag.has_attr('id'):
                    rendered['id'] = tag['id']

                if use_pre:
                    if generate_pdf:
                        pdf = get_ast_as_pdf(source_code, parse_expr)
                        if tag.has_attr('id'):
                            basename = tag['id']
                        else:
                            hashcode = hashlib.sha224(source_code).hexdigest()[-8:]
                            basename = 'code-%s' % (hashcode)

                        docname = os.path.splitext(os.path.basename(realpath))[0]
                        download = docname + '.' + basename + '.source_code.pdf'
                        a = create_a_to_data(download=download,
                                             data_format='pdf', data=pdf)
                        a['class'] = 'pdf_data'
                        a.append(NavigableString(download))
                        div = Tag(name='div')
                        div.append(rendered)
                        div.append(a)
                        tag.replaceWith(div)
                    else:
                        tag.replaceWith(rendered)
                else:
                    tag.replaceWith(rendered)

            except DPSyntaxError as e:
                if raise_errors:
                    raise
                logger.error(unicode(e.__str__(), 'utf-8'))
                t = Tag(name='pre', **{'class': 'error %s' % type(e).__name__})
                t.string = str(e)
                tag.insert_after(t)

                if tag.string is None:
                    tag.string = "`%s" % tag['id']

            except DPSemanticError as e:
                if raise_errors:
                    raise
                logger.error(unicode(e.__str__(), 'utf-8'))
                t = Tag(name='pre', **{'class': 'error %s' % type(e).__name__})
                t.string = str(e)
                tag.insert_after(t)
                if tag.string is None:
                    tag.string = "`%s" % tag['id']
                    
            except DPInternalError as e:
                msg = 'Error while interpreting the code:\n\n'
                msg += indent(source_code, '  | ')
                raise_wrapped(DPInternalError, e,msg, exc=sys.exc_info())
                
    # <k>A</k> ==> <code class=keyword>A</code>
    for e in soup.select('k'):
        e2 = Tag(name='code')
        copy_string_and_attrs(e, e2)
        # THEN add class
        add_class(e2, 'keyword')
        e.replace_with(e2)
        
    # <program>A</program> ==> <code class=program>A</code>
    for e in soup.select('program'):
        e2 = Tag(name='code')
        # copy string
        copy_string_and_attrs(e, e2)
        # THEN add class
        add_class(e2, 'program')
        e.replace_with(e2)
         
#     'mcdp_template','mcdp', 'mcdp_statements',
    # mcdp-poset
#     print('initial mcdp_value: %s' % len(list(soup.select('code.mcdp_value'))))
#     print('initial mcdp_poset: %s' % len(list(soup.select('code.mcdp_poset'))))
    for x in [ 
        'mcdp_poset', 
        'mcdp_fvalue',
        'mcdp_rvalue', 'mcdp_value']:
        # mcdp_poset -> mcdp-poset
        corresponding = x.replace('_', '-')
             
        for e in soup.select(corresponding):
            e2 = Tag(name='code')
            copy_string_and_attrs(e, e2)
            # THEN add class
            add_class(e2, x)

#             print('%s -> %s' % (e, e2))
#             
            e.replace_with(e2)
    
    # this is a bug with bs4. The replace_with above only adds an escaped
    # text rather than the actual tag (!).
    soup = bs(to_html_stripping_fragment(soup)) 
    assert soup.name == 'fragment'       
#     print('final code.mcdp_poset: %s' % len(list(soup.select('code.mcdp_poset'))))
#     print('final code.mcdp_value: %s' % len(list(soup.select('code.mcdp_value'))))
    
    
    
    go('pre.mcdp', Syntax.ndpt_dp_rvalue,  "mcdp", use_pre=True, refine=parse_ndp_refine)
    go('pre.mcdp_poset', Syntax.space, "mcdp_poset", use_pre=True, refine=parse_poset_refine)
    go('pre.mcdp_template', Syntax.template, "mcdp_template", use_pre=True,
        refine=parse_template_refine)
       
    go('pre.mcdp_statements', Syntax.dp_model_statements, "mcdp_statements", use_pre=True)
    go('pre.mcdp_fvalue', Syntax.fvalue, "mcdp_fvalue", use_pre=True)
    go('pre.mcdp_rvalue', Syntax.rvalue, "mcdp_rvalue", use_pre=True)
    # todo: add deprecation
    go('pre.mcdp_value', Syntax.rvalue, "mcdp_value", use_pre=True)

    go('code.mcdp', Syntax.ndpt_dp_rvalue, "mcdp", use_pre=False)
    go('code.mcdp_poset', Syntax.space, "mcdp_poset", use_pre=False)
    go('code.mcdp_value', Syntax.rvalue, "mcdp_value", use_pre=False)
    go('code.mcdp_template', Syntax.template, "mcdp_template", use_pre=False)


#     compute_size_for_pre_without_class(soup)

    # this is a bug with bs4...
    for pre in soup.select('pre + pre'):
#         print('adding br between PREs')
        br = Tag(name='br')
        br['class'] = 'pre_after_pre'
        pre.parent.insert(pre.parent.index(pre), br)
  
  
  
    res = to_html_stripping_fragment(soup)
#     print 'highlight_mcdp_code: %s' % res
    return res

def copy_string_and_attrs(e, e2):
    if e.string is not None:
        e2.string = e.string
    # copy attributes
    for k, v in e.attrs.items():
        e2[k] = v
#                 
# def add_br_before_pres(html):
#     soup = bs(html)
#     pres = list(soup.select('pre'))
# #     print('pres: %d %s' %(len(pres), pres))
#     for pre in pres:
#         p = pre.previousSibling
#         if p is not None:
#             if isinstance(p, NavigableString):
#                 if '\n' in p:
# #                     print('pre: %s' % str(pre))
# #                     print 'soup', soup
# #                     print 'soup dict', soup.__dict__
# #                     print 'soup.parser_class.new_tag', soup.parser_class.new_tag
#                     br =Tag(name='br')
#                     br.string = ''
#                     br['class'] = 'added_before_pre'
#                     br['orig'] = unicode(p).__repr__()
#                     br['reference'] = "pre: %s p: %s" % (str(id(pre)), str(id(p)))
# #                     print  br['reference']
# #                     print('adding tag br')
# #                     pre.insert_before(br)
#                     pre.parent.insert(pre.parent.index(pre), br)
#     return to_html_stripping_fragment(soup)

def add_class(e, c):
    if isinstance(c, str):    
        cc = c.split(' ')
    elif isinstance(c, list):
        cc = c
    else:
        raise ValueError(c)
    cur = e.get('class', [])
    if isinstance(cur, str):
        cur = cur.split()
    cur = cur + cc
    e['class'] = cur
#     print 'old %s new %s attr %s ' %(cur, n, e['class'])

# def compute_size_for_pre_without_class(soup):
#     for pre in soup.select('pre'):
#         if not pre.has_attr('class'):
#             s = ''.join(pre.findAll(text=True))
#             max_len = max_len_of_pre_html(s)
#             add_style_for_size(pre, max_len)

# think of :[[space]] × [[space]] × [["..."]] × [[space]]
def max_len_of_pre_html(html):
    from mcdp_report_ndp_tests.test0 import project_html
    source2 = project_html(html)
    line_len = lambda _: len(unicode(_, 'utf-8').rstrip())
    max_len = max(map(line_len, source2.split('\n')))
    return max_len 
# 
# def add_style_for_size(element, max_len):         
#     fontsize = 14 # px
#     fontsize = 8
#     padding = 30
#     fontname = 'Courier'
#     ratio = 0.65 # ratio for Courier font
#     width = fontsize * (max_len) * ratio + padding
#     style = 'font-family: %s; font-size: %spx; width: %dpx;' % (fontname, fontsize, width)
#     
#     if not element.has_attr('style'):
#         element['style'] = ''
# #         
# #         style = element['style'] +';' + style
# #             
# 
#     if True:
#         style = 'display: inline-block'
#         
#     element['style']+=  ';' + style
#     

@contract(frag=str, returns=str)
def make_figures(library, frag, raise_error_dp, raise_error_others, realpath, generate_pdf):
    """ Looks for codes like:

    <pre><code class="mcdp_ndp_graph_templatized">mcdp {
        # empty model
    }
    </code></pre>
    
        and creates a link to the image
    """

    soup = bs(frag)

    def go(selector, func):

        for tag in soup.select(selector):
            try:
                r = func(tag) 
                tag.replaceWith(r)
            except (DPSyntaxError, DPSemanticError) as e:
                if raise_error_dp:
                    raise
                logger.error(e)
                t = Tag(name='pre', **{'class': 'error %s' % type(e).__name__})
                t.string = str(e)
                tag.insert_after(t)
            except Exception as e:
                if raise_error_others:
                    raise
                t = Tag(name='pre', **{'class': 'error %s' % type(e).__name__})
                t.string = traceback.format_exc(e)
                tag.insert_after(t)
     

    def make_tag(tag0, klass, data, ndp=None, template=None, poset=None):
        svg = data['svg']

        tag_svg = BeautifulSoup(svg, 'lxml', from_encoding='utf-8').svg
        
        assert tag_svg.name == 'svg'
        if tag_svg.has_attr('width'):
            ws = tag_svg['width']
            hs = tag_svg['height']
            assert 'pt' in ws
            w = float(ws.replace('pt',''))
            h = float(hs.replace('pt',''))
            scale = MCDPConstants.scale_svg 
            
            w2 = w * scale
            h2 = h * scale
            tag_svg['width'] = w2
            tag_svg['height'] = h2
            tag_svg['rescaled'] = 'Rescaled from %s %s, scale = %s' % (ws, hs, scale)
        else:
            print('no width in SVG tag: %s' % tag_svg)
            
            
        tag_svg['class'] = klass

        if tag0.has_attr('style'):
            tag_svg['style'] = tag0['style']
        if tag0.has_attr('id'):
            tag_svg['id'] = tag0['id']

        if generate_pdf:
            pdf0 = data['pdf']
            pdf = crop_pdf(pdf0, margins=0)

            div = Tag(name='div')

            if tag0.has_attr('id'):
                basename = tag0['id']
            elif ndp is not None and hasattr(ndp, ATTR_LOAD_NAME):
                basename = getattr(ndp, ATTR_LOAD_NAME)
            elif template is not None and hasattr(template, ATTR_LOAD_NAME):
                basename = getattr(template, ATTR_LOAD_NAME)
            elif poset is not None and hasattr(poset, ATTR_LOAD_NAME):
                basename = getattr(poset, ATTR_LOAD_NAME)
            else:
                hashcode = hashlib.sha224(tag0.string).hexdigest()[-8:]
                basename = 'code-%s' % (hashcode)

            docname = os.path.splitext(os.path.basename(realpath))[0]
            download = docname + "." + basename + "." + klass + '.pdf'
            a = create_a_to_data(download=download, data_format='pdf', data=pdf)
            a['class'] = 'pdf_data'
            a.append(NavigableString(download))
            div.append(tag_svg)
            div.append(a)
            return div
        else:
            return tag_svg

    
    mf = MakeFiguresNDP(None, None, None)
    available_ndp = set(mf.available()) | set(mf.aliases)
    for which in available_ndp:
        def callback(tag0):
            context = Context()
            load = lambda x: library.load_ndp(x, context=context)
            parse = lambda x: library.parse_ndp(x, realpath=realpath, context=context)  
            ndp = load_or_parse_from_tag(tag0, load, parse)

            mf = MakeFiguresNDP(ndp=ndp, library=library, yourname=None) # XXX
            formats = ['svg']
            if generate_pdf: 
                formats.append('pdf')
            data = mf.get_figure(which,formats)
            tag = make_tag(tag0, which, data, ndp=ndp, template=None)
            return tag
        
        selector = 'render.%s' % which
        go(selector, callback)
        selector = 'pre.%s' % which
        go(selector, callback)
        selector = 'img.%s' % which
        go(selector, callback)
    
    mf = MakeFiguresTemplate(None,None,None)
    available_template = set(mf.available()) | set(mf.aliases)
    for which in available_template:
        def callback(tag0):
            context = Context()
            load = lambda x: library.load_template(x, context=context)
            parse = lambda x: library.parse_template(x, realpath=realpath, context=context)  
            template = load_or_parse_from_tag(tag0, load, parse)

            mf = MakeFiguresTemplate(template=template, library=library, yourname=None) # XXX
            formats = ['svg']
            if generate_pdf: 
                formats.append('pdf')
            data = mf.get_figure(which,formats)
            tag = make_tag(tag0, which, data, ndp=None, template=template)
            return tag
        
        selector = 'pre.%s' % which
        go(selector, callback)
        selector = 'img.%s' % which
        go(selector, callback)
        selector = 'render.%s' % which
        go(selector, callback)
        
    mf = MakeFiguresPoset(None)
    available_poset = set(mf.available()) | set(mf.aliases)
    for which in available_poset:
        def callback(tag0):
            context = Context()
            load = lambda x: library.load_poset(x, context=context)
            parse = lambda x: library.parse_poset(x, realpath=realpath, context=context)  
            poset = load_or_parse_from_tag(tag0, load, parse)
            
            mf = MakeFiguresPoset(poset=poset, library=library)
            formats = ['svg']
            if generate_pdf: 
                formats.append('pdf')
            data = mf.get_figure(which, formats)
            tag = make_tag(tag0, which, data, ndp=None, template=None, poset=poset)
            return tag
        
        selector = 'pre.%s' % which
        go(selector, callback)
        selector = 'img.%s' % which
        go(selector, callback)
        selector = 'render.%s' % which
        go(selector, callback)


    unsure = list(soup.select('render'))
    if unsure:
        msg = 'Invalid "render" elements.'
        msg += '\n\n' + '\n\n'.join(str(_) for _ in unsure)
        
        msg += '\n\n' + " Available for NDPs: %s." % ", ".join(sorted(available_ndp))
        msg += '\n\n' + " Available for templates: %s." % ", ".join(sorted(available_template))
        msg += '\n\n' + " Available for posets: %s." % ", ".join(sorted(available_poset))
        raise ValueError(msg)
    return to_html_stripping_fragment(soup)

@contract(data_format=str, data=str, download=str)
def create_a_to_data(download, data_format, data):
    """ Returns a tag with base64 encoded data """
    assert data_format in ['pdf', 'png']
    mime = get_mime_for_format(data_format)
    encoded = base64.b64encode(data)
    href = 'data:%s;base64,%s' % (mime, encoded)
    attrs = dict(href=href, download=download)
    return Tag(name='a', attrs=attrs)

def create_img_png_base64(png, **attrs):
    encoded = base64.b64encode(png)
    src = 'data:image/png;base64,%s' % encoded
    attrs = dict(**attrs)
    attrs['src'] =src
    return Tag(name='img', attrs=attrs)

def bool_from_string(b):
    yes = ['True', 'true', '1', 'yes']
    no = ['False', 'false', '0', 'no']
    if b in yes:
        return True
    if b in no:
        return False
    msg = 'Cannot interpret string as boolean.'
    raise_desc(ValueError, msg, b=b)
    

