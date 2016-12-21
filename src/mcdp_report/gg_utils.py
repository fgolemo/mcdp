# -*- coding: utf-8 -*-
""" Utils for graphgen """

import base64
import codecs
from contextlib import contextmanager
from copy import deepcopy
import os
import traceback

from bs4 import BeautifulSoup

from contracts import contract
from contracts.utils import check_isinstance, raise_desc
from mcdp_library_tests.tests import timeit_wall
from mocdp import logger, MCDPConstants
from mocdp.exceptions import mcdp_dev_warning
import networkx as nx  # @UnresolvedImport
from reprep.constants import MIME_PDF, MIME_PLAIN, MIME_PNG, MIME_SVG
from system_cmd import CmdException, system_cmd_result
from tempfile import mkdtemp
import shutil
import cStringIO
import re



def graphviz_run(filename_dot, output, prog='dot'):
    suff = os.path.splitext(output)[1][1:]
    if not suff in ['png', 'pdf', 'ps', 'svg']:
        raise ValueError((output, suff))

    encoder = suff

    cmd = [prog, '-T%s' % encoder, '-o', output, filename_dot]
    
#     system_cmd_result(cwd='.', cmd=['cp', filename_dot, 'last_processed.dot'])
#     print('just before running graphviz')
    with timeit_wall('running graphviz on %s' % filename_dot, 1.0):
        try:
            # print('running graphviz')
            system_cmd_result(cwd='.', cmd=cmd,
                     #display_stdout=False,
                     display_stdout=True,
                     #display_stderr=False,
                     display_stderr=True,
                     raise_on_error=True,
                     )
            # print('done')
        except (CmdException, KeyboardInterrupt):
            emergency = 'emergency.dot'
            logger.error('saving to %r' % emergency)  # XXX
            contents = open(filename_dot).read()
            with open(emergency, 'w') as f:
                f.write(contents)
            # print(contents)
            raise
    

def gg_deepcopy(ggraph):
    try:
        return deepcopy(ggraph)
    except Exception as e:
        print traceback.format_exc(e)
        mcdp_dev_warning('Deep copy of gvgen graph failed: happens when in IPython.')
        return ggraph


def graphvizgen_plot(ggraph, output, prog='dot'):
    gg = gg_deepcopy(ggraph)
    with tmpfile(".dot") as filename_dot:
        with open(filename_dot, 'w') as f:
            gg.dot(f)
        try:
            graphviz_run(filename_dot, output, prog=prog)
        except:
            contents = open(filename_dot).read()
            import hashlib
            m = hashlib.md5()
            m.update(contents)
            s = m.hexdigest()
            filename = 'out-%s.dot' % s
            with open(filename, 'w') as f:
                f.write(contents)
            print('Saved problematic dot as %r.' % filename)
            raise

def nx_generic_graphviz_plot(G, output, prog='dot'):
    """ Converts to dot and writes on the file output """
    with tmpfile(".dot") as filename_dot:
        nx.write_dot(G, filename_dot)  # @UndefinedVariable
        graphviz_run(filename_dot, output, prog=prog)

def get_dot_string(gg):
    with tmpfile(".dot") as filename_dot:
        if False:
            with open(filename_dot, 'w') as fo:
                gg.dot(fo)
            contents = open(filename_dot).read()
        else:
            contents = gg.dot2()
        contents = contents.replace('"<TABLE', '<<TABLE')
        contents = contents.replace('</TABLE>"', '</TABLE>>')
        return contents


def gg_figure(r, name, ggraph, do_png=True, do_pdf=True, do_svg=True,
              do_dot=True):
    """ Adds a figure to the Report r that displays this graph
        and also its source. """
    f = r.figure(name, cols=1)

    # save file in dot file
    with tmpfile(".dot") as filename_dot:
        with open(filename_dot, 'w') as fo:
            s = get_dot_string(ggraph)
            fo.write(s)

#         if False:
#             ff = '%s.dot' % id(r)
#             print('writing to %r' % ff)
#             with open(ff, 'w') as f2:
#                 f2.write(s)

        prog = 'dot'
        try:
                
            if do_png:
                with f.data_file('graph', MIME_PNG) as filename:
                    graphviz_run(filename_dot, filename, prog=prog)
    
            if do_pdf:
                with f.data_file('graph_pdf', MIME_PDF) as filename:
                    graphviz_run(filename_dot, filename, prog=prog)
    
            if do_svg:
                with f.data_file('graph_svg', MIME_SVG) as filename:
                    graphviz_run(filename_dot, filename, prog=prog)
    
                    soup = BeautifulSoup(open(filename).read(), 'lxml', from_encoding='utf-8')
                    for tag in soup.select('image'):
                        href = tag['xlink:href']
                        extensions = ['png', 'jpg']
                        for ext in extensions:
                            if ext in href:
                                with open(href) as ff:
                                    png = ff.read()
                                encoded = base64.b64encode(png)
                                from mcdp_web.images.images import get_mime_for_format
                                mime = get_mime_for_format(ext)
                                src = 'data:%s;base64,%s' % (mime, encoded)
                                tag['xlink:href'] = src
    
                    with codecs.open(filename, 'w', encoding='utf-8') as ff:
                        s = str(soup)
                        u = unicode(s, 'utf-8')
                        ff.write(u)
        except CmdException:
            if MCDPConstants.test_ignore_graphviz_errors:
                mcdp_dev_warning('suppressing errors from graphviz')
                logger.error('Graphivz failed, but I will ignore it '
                             'because of MCDPConstants.test_ignore_graphviz_errors.')
            else:
                raise

        # MIME_GRAPHVIZ
        if do_dot:
            with f.data_file('dot', MIME_PLAIN) as filename:
                with open(filename, 'w') as f:
                    f.write(s)
        
    return f

allowed_formats = ['png', 'pdf', 'svg', 'dot']

@contract(returns='tuple')
def gg_get_formats(gg, data_formats):
    check_isinstance(data_formats, (list, tuple))
    res = []
    mcdp_dev_warning('TODO: optimize gg_get_formats')
    for data_format in data_formats:
        if not data_format in allowed_formats:
            msg = 'Invalid data format.' 
            raise_desc(ValueError, msg, data_formats=data_formats)

        if data_format == 'dot':
            d = get_dot_string(gg)
        else:
            d = gg_get_format(gg, data_format)

        res.append(d)
    return tuple(res)
 
     
    
def gg_get_format(gg, data_format):
    from reprep import Report
    r = Report()
    do_dot = data_format == 'dot'
    do_png = data_format == 'png'
    do_pdf = data_format == 'pdf'
    do_svg = data_format == 'svg'
#     from mcdp_library_tests.tests import timeit_wall
    with timeit_wall('gg_figure %s' % data_format): 
        gg_figure(r, 'graph', gg, do_dot=do_dot,
                    do_png=do_png, do_pdf=do_pdf, do_svg=do_svg)

    if data_format == 'pdf':
        pdf = r.resolve_url('graph_pdf').get_raw_data()
        return pdf
    elif data_format == 'png':
        png = r.resolve_url('graph/graph').get_raw_data()
        return png
    elif data_format == 'dot':
        dot = r.resolve_url('dot').get_raw_data()
        return dot
    elif data_format == 'svg':
        svg = r.resolve_url('graph_svg').get_raw_data()
        return svg
    else:
        raise ValueError('No known format %r.' % data_format)

def embed_images(html, basedir):
    """ Embeds png and Jpg images using data """
    soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    for tag in soup.select('img'):
        href = tag['src']
        extensions = ['png', 'jpg']
        for ext in extensions:
            if ext in href and not 'data:' in href:
                resolve = os.path.join(basedir, href)
                with open(resolve) as ff:
                    data = ff.read()
                encoded = base64.b64encode(data)
                from mcdp_web.images.images import get_mime_for_format
                mime = get_mime_for_format(ext)
                src = 'data:%s;base64,%s' % (mime, encoded)
                tag['src'] = src
    return str(soup)

def embed_images_from_library(html, library):
    """ Resolves images from library """
    from mcdp_web.renderdoc.xmlutils import bs, to_html_stripping_fragment
    def resolve(href):
        #print('resolving %r' % href)
        f = library._get_file_data(href)
        data = f['data']
        # realpath = f['realpath']
        return data

    from mcdp_web.images.images import get_mime_for_format
        
        
    soup = bs(html)
    assert soup.name == 'fragment'
    # first, convert pdf to png
    for tag in soup.select('img[src$=pdf], img[src$=PDF]'):
        # load pdf data
        data_pdf = resolve(tag['src'])

        density = MCDPConstants.pdf_to_png_dpi # dots per inch
        data_png = png_from_pdf(data_pdf, density=density)
        
        # get png image size
        from PIL import Image
        im=Image.open(cStringIO.StringIO(data_png))
        width_px, height_px = im.size # (width,height) tuple
        width_in = width_px / float(density)
        height_in = height_px / float(density)
        
        scale = 1.0
        if tag.has_attr('latex-options'):
            o = tag['latex-options']
#             print('latex options: %r' % o)
            if 'scale' in o:
#                 print('warning: no scale in latex options')
                tokens = re.split(',|=', o)
#                 print('tokens %s' % tokens)
                scale_token = tokens[1+tokens.index('scale')]
                scale = float(scale_token)
            print('%s -> %s' % (o, scale))
        use_width_in = width_in * scale
        use_height_in = height_in * scale
        # now, let's work out the original size
        sizing = 'width: %sin; height: %sin;' % (use_width_in, use_height_in)
        s = tag['style'] + ';' if tag.has_attr('style') else ''
        tag['style'] = s + sizing
        tag['size_in_pixels'] = '%s, %s' % (width_px, height_px)
        # encode
        encoded = base64.b64encode(data_png)
        mime = get_mime_for_format('png')
        src = 'data:%s;base64,%s' % (mime, encoded)
        tag['src'] = src
        
        
    for tag in soup.select('img'):
        href = tag['src']
        img_extensions = ['png', 'jpg', 'PNG', 'JPG', 'svg', 'SVG']
        for ext in img_extensions:
            if ext in href and not 'data:' in href:
                data = resolve(href)
                encoded = base64.b64encode(data) 
                mime = get_mime_for_format(ext)
                src = 'data:%s;base64,%s' % (mime, encoded)
                tag['src'] = src
                
    return to_html_stripping_fragment(soup)
    
    
def png_from_pdf(pdf_data, density):
    d = mkdtemp()
    try:
        tmpfile = os.path.join(d, 'file.pdf')
        with open(tmpfile, 'wb') as f:
            f.write(pdf_data)
        
        out = os.path.join(d, 'file.png')
    
        cmd = [
            'convert',
            '-density', str(density), 
            '-background', 'white',
            '-alpha','remove',
            '-alpha','off', 
            tmpfile, 
            out
        ]
        try:
            system_cmd_result(cwd='.', cmd=cmd,
                     display_stdout=False,
                     display_stderr=False,
                     raise_on_error=True)

        except CmdException:
            raise
        
        r = open(out,'rb').read()
        return r
    finally:
        shutil.rmtree(d)
        
def extract_assets(html, basedir):
    """ Extracts all embedded assets. """
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    for tag in soup.select('a'):
        href = tag['href']
        if href.startswith('data:'):
            _mime, data = link_data(href)
#             from mcdp_web.images.images import get_ext_for_mime
#             ext = get_ext_for_mime(mime)
            if tag.has_attr('download'):
                basename = tag['download']
            else:
                print('cannot find attr "download" in tag')
                # print tag
                continue
            filename = os.path.join(basedir, basename)
            with open(filename, 'w') as f:
                f.write(data)
            print('written to %s' % filename)

@contract(returns='tuple(str,str)')
def link_data(data_ref):
    """ data_ref: data:<mime>;base64, 
    
        Returns mime, data.
    """
    assert data_ref.startswith('data:')
    first, second = data_ref.split(';')
    mime = first[len('data:'):]
    assert second.startswith('base64,')
    data = second[len('base64,'):]
    # print('link %r' % data_ref[:100])
    # print('decoding %r' % data[:100])
    decoded = base64.b64decode(data)
    return mime, decoded




@contextmanager
def tmpfile(suffix):
    """ Yields the name of a temporary file """
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix)
    yield temp_file.name
    temp_file.close()
