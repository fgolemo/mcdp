""" Utils for graphgen """

from bs4 import BeautifulSoup
from contextlib import contextmanager
from copy import deepcopy
from mocdp.exceptions import mcdp_dev_warning
from reprep.constants import MIME_PDF, MIME_PLAIN, MIME_PNG, MIME_SVG
from system_cmd import CmdException, system_cmd_result
import base64
import codecs
import networkx as nx  # @UnresolvedImport
import os
import traceback
from contracts import contract



def graphviz_run(filename_dot, output, prog='dot'):
    suff = os.path.splitext(output)[1][1:]
    if not suff in ['png', 'pdf', 'ps', 'svg']:
        raise ValueError((output, suff))

    encoder = suff

    cmd = [prog, '-T%s' % encoder, '-o', output, filename_dot]
    try:
        # print('running graphviz')
        system_cmd_result(cwd='.', cmd=cmd,
                 display_stdout=False,
                 display_stderr=False,
                 raise_on_error=True)
        # print('done')
    except (CmdException, KeyboardInterrupt):
        emergency = 'emergency.dot'
        print('saving to %r' % emergency)  # XXX
        contents = open(filename_dot).read()
        with open(emergency, 'w') as f:
            f.write(contents)
        print(contents)
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
        if do_png:
            with f.data_file('graph', MIME_PNG) as filename:
                graphviz_run(filename_dot, filename, prog=prog)

        if do_pdf:
            with r.data_file('graph_pdf', MIME_PDF) as filename:
                graphviz_run(filename_dot, filename, prog=prog)

        if do_svg:
            with r.data_file('graph_svg', MIME_SVG) as filename:
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

        # MIME_GRAPHVIZ
        if do_dot:
            with f.data_file('dot', MIME_PLAIN) as filename:
                with open(filename, 'w') as f:
                    f.write(s)
        
    return f

allowed_formats = ['png', 'pdf', 'svg', 'dot']

def gg_get_formats(gg, data_formats):
    res = []
    mcdp_dev_warning('TODO: optimize')
    for data_format in data_formats:
        if not data_format in allowed_formats:
            raise ValueError(data_format)

        if data_format == 'dot':
            d = get_dot_string(gg)
        else:
            d = gg_get_format(gg, data_format)

        res.append(d)
    return res

def gg_get_format(gg, data_format):
    from reprep import Report
    r = Report()
    do_dot = data_format == 'dot'
    do_png = data_format == 'png'
    do_pdf = data_format == 'pdf'
    do_svg = data_format == 'svg'
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

def extract_assets(html, basedir):
    """ Extracts all embedded assets. """
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    for tag in soup.select('a'):
        href = tag['href']
        if href.startswith('data:'):
            mime, data = link_data(href)
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
