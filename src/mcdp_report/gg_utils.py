""" Utils for graphgen """

from contextlib import contextmanager
from copy import deepcopy
from mocdp.exceptions import mcdp_dev_warning
from reprep.constants import MIME_PDF, MIME_PNG, MIME_PLAIN, MIME_SVG
from system_cmd import CmdException, system_cmd_result
import networkx as nx  # @UnresolvedImport
import os
import traceback
from bs4 import BeautifulSoup
import base64
import codecs


def graphviz_run(filename_dot, output, prog='dot'):
    suff = os.path.splitext(output)[1][1:]
    if not suff in ['png', 'pdf', 'ps', 'svg']:
        raise ValueError((output, suff))

    encoder = suff
#     if encoder == 'svg':
#         encoder = 'svg:cairo'

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


def gg_figure(r, name, ggraph):
    """ Adds a figure to the Report r that displays this graph
        and also its source. """
    f = r.figure(name, cols=1)

    # save file in dot file
    with tmpfile(".dot") as filename_dot:
        with open(filename_dot, 'w') as fo:
            s = get_dot_string(ggraph)
            fo.write(s)

        if False:
            ff = '%s.dot' % id(r)
            print('writing to %r' % ff)
            with open(ff, 'w') as f2:
                f2.write(s)

        prog = 'dot'
        with f.data_file('graph', MIME_PNG) as filename:
            graphviz_run(filename_dot, filename, prog=prog)

        with r.data_file('graph_pdf', MIME_PDF) as filename:
            graphviz_run(filename_dot, filename, prog=prog)

        with r.data_file('graph_svg', MIME_SVG) as filename:
            graphviz_run(filename_dot, filename, prog=prog)

            soup = BeautifulSoup(open(filename).read(), 'lxml')
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
# tag.replaceWith(rendered)

            with codecs.open(filename, 'w', encoding='utf-8') as ff:
                ff.write(soup.prettify())

        # MIME_GRAPHVIZ
        with f.data_file('dot', MIME_PLAIN) as filename:
            with open(filename, 'w') as f:
                f.write(s)
        
    return f


@contextmanager
def tmpfile(suffix):
    """ Yields the name of a temporary file """
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix)
    yield temp_file.name
    temp_file.close()
