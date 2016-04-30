from .utils_mkdir import mkdirs_thread_safe
from conf_tools import GlobalConfig
from conf_tools.utils import expand_string
from contracts import contract
from decent_params.utils import UserError
from mocdp.dp_report.gg_ndp import (STYLE_GREENRED, STYLE_GREENREDSYM,
    gvgen_from_ndp)
from mocdp.dp_report.gg_utils import get_dot_string, gg_figure
from mocdp.dp_report.report import gvgen_from_dp
from mocdp.exceptions import mcdp_dev_warning
from mocdp.lang.parse_actions import parse_ndp
from quickapp import QuickAppBase
from reprep import Report
from system_cmd import CmdException, system_cmd_result
from tempfile import mkdtemp
import os
from cdpview.solve_meat import solve_read_model
from mcdp_library.library import MCDPLibrary
from contracts.utils import raise_desc

def get_ndp(data):
    if not 'ndp' in data:
        dirs = data['dirs']
        param = data['model_name']
        library, basename, ndp = solve_read_model(dirs, param)
        data['ndp'] = ndp
    return data['ndp']

def get_dp(data):
    ndp = get_ndp(data)
    if not 'dp' in data:
        data['dp'] = ndp.get_dp()
    return data['dp']

def png_pdf_from_gg(gg):
    r = Report()
    gg_figure(r, 'graph', gg)
    png_node = r.resolve_url('graph/graph')
    pdf_node = r.resolve_url('graph_pdf')
    return png_node.get_raw_data(), pdf_node.get_raw_data()

def dp_visualization(data):
    dp = get_dp(data)
    gg = gvgen_from_dp(dp)
    png, pdf = png_pdf_from_gg(gg)
    res1 = ('png', 'dp_tree', png)
    res2 = ('pdf', 'dp_tree', pdf)
    return [res1, res2]

def ndp_visualization(data, style):
    ndp = get_ndp(data) 
    gg = gvgen_from_ndp(ndp, style)
    png, pdf = png_pdf_from_gg(gg)

    # do it again
    gg = gvgen_from_ndp(ndp, style)
    dot = get_dot_string(gg)

    res1 = ('png', style, png)
    res2 = ('pdf', style, pdf)
    res3 = ('dot', style, dot)

    return [res1, res2, res3]

def create_extra_css(params):
#     hide = params.get('hide', '')
#     lines = hide.split(':')
    out = ''
#     if not lines:
#         pass
#     else:
#         for l in lines:
#             out += 'span#line%s, ' % l
#         out += ' { display: none; }'
    return out

def get_lines_to_hide(params):
    hide = params.get('hide', '')
    if not hide:
        return []
    lines = hide.split(':')
    return [int(_) for _ in lines]

def syntax_pdf(data):
    from mocdp.dp_report.html import ast_to_html
    s = data['s']
    s = s.replace('\t', '    ')
    extra_css = create_extra_css(data['params'])
    lines_to_hide = get_lines_to_hide(data['params'])
    def ignore_line(lineno):
        return lineno  in lines_to_hide
    html = ast_to_html(s, complete_document=True, extra_css=extra_css,
                       ignore_line=ignore_line)

    d = mkdtemp()
    
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
          
        f_pdf_crop = os.path.join(d, 'file_crop.pdf')
        cmd = ['pdfcrop', '--margins', '4', f_pdf, f_pdf_crop]
        system_cmd_result(
                d, cmd, 
                display_stdout=False,
                display_stderr=False,
                raise_on_error=True)
    
        with open(f_pdf_crop) as f:
            data = f.read()
    
        f_png = os.path.join(d, 'file.png')
        cmd = ['convert', '-density', '600', f_pdf_crop,
                '-background', 'white', '-alpha', 'remove',
                '-resize', '50%', f_png]
        system_cmd_result(
                d, cmd,
                display_stdout=False,
                display_stderr=False,
                raise_on_error=True)
    
        with open(f_png) as f:
            pngdata = f.read()
    
        return [('pdf', 'syntax_pdf', data), ('png', 'syntax_pdf', pngdata)]
    except CmdException as e:
        raise e
        
@contract(data=dict)
def syntax_frag(data):
    from mocdp.dp_report.html import ast_to_html
    s = data['s']
    extra_css = create_extra_css(data['params'])
    res = ast_to_html(s, complete_document=False, extra_css=extra_css)
    res1 = ('html', 'syntax_frag', res)
    return [res1]

@contract(data=dict)
def syntax_doc(data):
    from mocdp.dp_report.html import ast_to_html
    s = data['s']
    extra_css = create_extra_css(data['params'])
    lines_to_hide = get_lines_to_hide(data['params'])
    def ignore_line(lineno):
        return lineno  in lines_to_hide

    res = ast_to_html(s, complete_document=True, extra_css=extra_css,
                      ignore_line=ignore_line)
    res1 = ('html', 'syntax_doc', res)
    return [res1]


@contract(data=dict)
def ast(data):
    s = data['s']
    from mocdp.dp_report.html import ast_to_text
    res = ast_to_text(s)
    res1 = ('txt', 'ast', res)
    return [res1]


def tex_form(data):
    filename = data['filename']
    d = os.path.dirname(filename)
    b = os.path.basename(filename)
    graphics = os.path.join(d, 'out', os.path.splitext(b)[0]) + '-syntax_pdf.pdf'
    graphics = os.path.realpath(graphics)
    res = """
    \\includegraphics{%s}
    """ % graphics
    res1 = ('tex', 'tex_form', res)
    return [res1]

allplots  = {
    ('ast', ast),
    ('syntax_doc', syntax_doc),
    ('syntax_frag', syntax_frag),
    ('syntax_pdf', syntax_pdf),
    ('dp_tree', dp_visualization),
    ('tex_form', tex_form),
}

class Vis():
    def __init__(self, s):
        self.s = s
    def __call__(self, data):
        return ndp_visualization(data, style=self.s)

for s in [STYLE_GREENRED, 'default', 'clean', STYLE_GREENREDSYM]:
    x = ('ndp_%s' % s, Vis(s))
    allplots.add(x)


@contract(returns='tuple(str,*)')
def parse_kv(x):
    return tuple(x.split('='))

def parse_params(p):
    p = p.strip()
    if not p:
        return {}
    seq = p.split(',')

    return dict(parse_kv(_) for _ in seq)

def do_plots(logger, model_name, plots, outdir, extra_params, dirs):
    data = {}

    data['dirs'] = dirs
    data['model_name'] = model_name

    GlobalConfig.global_load_dir("mocdp")

    library = MCDPLibrary()
    for d in dirs:
        library = library.add_search_dir(d)

    filename = model_name + '.mcdp'
    x = library._get_file_data(filename)
    data['s'] = x['data']
    data['filename'] = x['realpath']
    data['params'] = parse_params(extra_params)

    d = dict(allplots)
    results = []
    for p in plots:    
        # print('plotting %r ' % p)
        try:
            res = d[p](data)
        except CmdException as e:
            mcdp_dev_warning('Add better checks of error.')
            logger.error(e)
            continue
        assert isinstance(res, list), res
        for r in res:
            assert isinstance(r, tuple), r
            mime, name, x = r
            assert isinstance(x, str), x
            ext = mime

            base = model_name + '-%s.%s' % (name, ext)

            out = os.path.join(outdir, base)
            logger.info('Writing to %s' % out)
            with open(out, 'w') as f:
                f.write(x)

            results.append(r)

    return results



class PlotDP(QuickAppBase):
    """ Plot a DP:
    
        mcdp-plot [--watch] [--plots *] [--out outdir] [-d dir] model_name
        
    """

    def define_program_options(self, params):
        params.add_flag('watch')
        params.accept_extra()

        possible = [p for p, _ in allplots]

        params.add_string('out', help='Output dir', default=None)
        params.add_string('extra_params', help='Add extra params', default="")
        params.add_string('plots', default='*', help='One of: %s' % possible)

        params.add_string('dirs', default='.', short='-d',
                           help='Library directories containing models.')

    def go(self):
        GlobalConfig.global_load_dir("mocdp")

        options = self.get_options()
        filenames = options.get_extra()
        print options
        if len(filenames) == 0:
            raise_desc(UserError, 'Need at least one filename.', filenames=filenames)

        if len(filenames) > 1:
            raise_desc(NotImplementedError, 'Want only 1 filename.', filenames=filenames)

        filename = filenames[0]

        if options.out is None:
            out = os.path.dirname(filename)
            if not out:
                out = '.'
        else:
            out = options.out
        mkdirs_thread_safe(out)
        possible = [p for p, _ in allplots]
        plots = expand_string(options.plots, list(possible))
        logger = self.logger  # HasLogger
        dirs = options.dirs.split(':')
        do_plots(logger, filename, plots, out, options.extra_params, dirs=dirs)

        if options.watch:
            def handler():
                do_plots(filename, plots, out)

            from cdpview.go import watch
            d = os.path.dirname(filename)
            if d == '':
                d = '.'
            watch(path=d, handler=handler)


mcdp_plot_main = PlotDP.get_sys_main()

