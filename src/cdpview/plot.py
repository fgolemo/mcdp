from .utils_mkdir import mkdirs_thread_safe
from conf_tools import GlobalConfig
from conf_tools.utils import expand_string
from contracts import contract
from mocdp.dp_report.gg_ndp import gvgen_from_ndp
from mocdp.dp_report.gg_utils import gg_figure
from mocdp.dp_report.report import gvgen_from_dp
from mocdp.exceptions import mcdp_dev_warning
from mocdp.lang.parse_actions import parse_ndp
from quickapp import QuickAppBase
from reprep import Report
from system_cmd import CmdException, system_cmd_result
from tempfile import mkdtemp
import os

def get_ndp(data):
    if not 'ndp' in data:
        data['ndp'] = parse_ndp(data['s'])
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
    res1 = ('png', style, png)
    res2 = ('pdf', style, pdf)
    return [res1, res2]

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
    ('syntax_doc', syntax_doc),
    ('syntax_frag', syntax_frag),
    ('syntax_pdf', syntax_pdf),
    ('ndp_default', lambda data: ndp_visualization(data, 'default')),
    ('ndp_clean', lambda data: ndp_visualization(data, 'clean')),
    ('dp_tree', dp_visualization),
    ('tex_form', tex_form),
}

@contract(returns='tuple(str,*)')
def parse_kv(x):
    return tuple(x.split('='))

def parse_params(p):
    p = p.strip()
    if not p:
        return {}
    seq = p.split(',')

    return dict(parse_kv(_) for _ in seq)

def do_plots(filename, plots, outdir, extra_params):
    s = open(filename).read()
    data = {}
    data['filename'] = filename
    data['s'] = s
    data['params'] = parse_params(extra_params)

    d = dict(allplots)
    results = []
    for p in plots:    
        # print('plotting %r ' % p)
        try:
            res = d[p](data)
        except CmdException as e:
            mcdp_dev_warning('Add better checks of error.')
            print(e)
            pass
        assert isinstance(res, list)
        for r in res:
            assert isinstance(r, tuple), r
            mime, name, x = r
            assert isinstance(x, str), x
            ext = mime

            base = os.path.splitext(os.path.basename(filename))[0]
            base += '-%s.%s' % (name, ext)

            out = os.path.join(outdir, base)
            print('Writing to %s' % out)
            with open(out, 'w') as f:
                f.write(x)

            results.append(r)

    return results



class PlotDP(QuickAppBase):
    """ Plot a design program """
    def define_program_options(self, params):
        params.add_flag('watch')
        params.accept_extra()

        possible = [p for p, _ in allplots]


        params.add_string('out', help='Output dir', default=None)
        params.add_string('extra_params', help='Add extra params', default="")

        params.add_string('plots', default='*', help='One of: %s' % possible)

    def go(self):
        GlobalConfig.global_load_dir("mocdp")

        options = self.get_options()
        filenames = options.get_extra()

        if len(filenames) > 1:
            raise NotImplementedError('Only one filename')

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
        do_plots(filename, plots, out, options.extra_params)

        if options.watch:
            def handler():
                do_plots(filename, plots, out)

            from cdpview.go import watch
            watch(path=os.path.dirname(options.filename), handler=handler)


mcdp_plot_main = PlotDP.get_sys_main()

