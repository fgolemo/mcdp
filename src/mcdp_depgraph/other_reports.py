# -*- coding: utf-8 -*-
import os

from mcdp import logger
from contracts import contract
from mcdp_cli.plot import allplots
from mcdp_lang.syntax import Syntax
from mcdp_library import Librarian
from mcdp_report.gdc import STYLE_GREENREDSYM
from mcdp_docs.highlight import get_ast_as_pdf
from mcdp.exceptions import DPSemanticError
from system_cmd import CmdException

from .find_dep import EntryNDP, EntryTemplate, FindDependencies
from mcdp_web.editor_fancy.image import ndp_template_graph_enclosed
from mcdp_library.specs_def import SPEC_TEMPLATES


@contract(config_dirs='list(str)', outdir='str', maindir='str')
def other_jobs(context, maindir, config_dirs, outdir, res):
    fd = res['fd']
    assert isinstance(fd, FindDependencies)

    G = fd.create_graph()
    
    texs = []
    nodes = list(G.nodes())
    
    for entry in nodes:

        tex = context.comp(other_reports,
                     maindir=maindir,
                     config_dirs=config_dirs,
                     outdir=outdir,
                     entry=entry)#, job_id='other_reports-%s-%s' % (entry.libname, entry.name))
        texs.append(tex)

    context.comp(write_tex, outdir, texs)

def write_tex(outdir, texs):
    fn = os.path.join(outdir, 'all.tex')
    with open(fn, 'w') as f:
        for t in texs:
            if t is None:
                continue
            f.write(t)
    print('written {} '.format(fn))


@contract(config_dirs='list(str)', outdir='str', maindir='str')
def other_reports(outdir, maindir, config_dirs, entry):
    print('config dirs: {}'.format(config_dirs))
    librarian = Librarian()
    for e in config_dirs:
        librarian.find_libraries(e)

    default_library = librarian.get_library_by_dir(maindir)

    tex = ''

    library = default_library.load_library(entry.libname)

    if isinstance(entry, EntryTemplate):
        context = library._generate_context_with_hooks()
        template = library.load_spec(SPEC_TEMPLATES, entry.name, context)
        pdf = ndp_template_graph_enclosed(library=library, template=template,
                                    style=STYLE_GREENREDSYM, yourname=None,
                                    data_format='pdf', direction='TB', enclosed=True)
        base = entry.libname + '-' + entry.name + '-ndp_template_graph_enclosed.pdf'
        out = os.path.join(outdir, base)
        write_to_file(out, pdf)
        tex += '\n\\includegraphics{%s}' % base

        source_code = library._get_file_data(entry.name +'.mcdp_template')['data']
        code_pdf = get_ast_as_pdf(s=source_code, parse_expr=Syntax.template)

        base = entry.libname + '-' + entry.name + '-syntax_pdf.pdf'
        out = os.path.join(outdir, base)
        write_to_file(out, code_pdf)
        tex += '\n\\includegraphics{%s}' % base

    if isinstance(entry, EntryNDP):
        
        
        filename = entry.name + '.mcdp'
        x = library._get_file_data(filename)
        data = {}
        data['model_name'] = entry.name
        data['s'] = x['data'].strip()
        data['filename'] = x['realpath']
        data['params'] = {}
        data['library'] = library

        d = dict(allplots)
        plots = list(d.keys())
        plots.remove('ndp_clean')
        plots.remove('ndp_default')
        plots.remove('ndp_greenred')
        plots.remove('dp_graph_tree_compact_labeled')
#         plots.remove('dp_graph_compact_labeled')


        for p in plots:
            # print('plotting %r ' % p)
            try:
                res = d[p](data)
            except DPSemanticError as e:
                logger.error(str(e))
                continue
            except CmdException as e:
                logger.error(str(e))
                continue
            assert isinstance(res, list), res
            for r in res:
                assert isinstance(r, tuple), r
                mime, name, x = r
                assert isinstance(x, str), x
                ext = mime

                base = entry.libname + '-' + entry.name + '-%s.%s' % (name, ext)
                out = os.path.join(outdir, base)
                write_to_file(out, x)
                if ext == 'pdf':
                    tex += '\n\\includegraphics{%s}' % base


    print('outdir: %s' % outdir)
    print('entry: {}'.format(entry))

    return tex

def write_to_file(out, contents):
    dn = os.path.dirname(out)
    if not os.path.exists(dn):
        os.makedirs(dn)

    with open(out, 'w') as f:
        f.write(contents)
    print('Writing to %s' % out)
