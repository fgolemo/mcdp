# -*- coding: utf-8 -*-
from contracts.enabling import disable_all
from contracts.utils import raise_desc
from decent_params.utils.script_utils import UserError
from mcdp_library import Librarian, MCDPLibrary
from mcdp_report.gg_utils import embed_images_from_library
from mcdp_web.renderdoc.highlight import get_minimal_document
from mcdp_web.renderdoc.main import render_complete
from mocdp import logger
from quickapp import QuickAppBase
import logging
import os


class Render(QuickAppBase):
    """ Evaluates one of the constants """

    def define_program_options(self, params):
        params.add_string('out', help='Output dir', default=None)

        params.accept_extra()
        params.add_flag('cache')
        params.add_flag('contracts')
        params.add_flag('pdf', help='Generate PDF version of code and figures.')

        params.add_string('config_dirs', default='.', short='-D',
                           help='Other libraries.')
        params.add_string('maindir', default='.', short='-d',
                           help='Library directories containing models, separated by :.')

    def go(self):
        logger.setLevel(logging.DEBUG)

        options = self.get_options()

        if not options.contracts:
            disable_all()

        params = options.get_extra()

        if len(params) < 1:
            raise ValueError('Please specify name.')

        config_dirs = options.config_dirs.split(":")
        maindir = options.maindir
        out_dir = options.out

        if out_dir is None:
            out_dir = os.path.join('out', 'mcdp_render')

        if options.cache:
            cache_dir = os.path.join(out_dir, '_cached', 'solve')
        else:
            cache_dir = None

        librarian = Librarian()
        for e in config_dirs:
            librarian.find_libraries(e)

        library = librarian.get_library_by_dir(maindir)
        if cache_dir is not None:
            library.use_cache_dir(cache_dir)

        docs = params

        if not docs:
            msg = 'At least one argument required.'
            raise_desc(UserError, msg)

        for docname in docs:
            basename = docname + '.' + MCDPLibrary.ext_doc_md
            f = library._get_file_data(basename)
            data = f['data']
            realpath = f['realpath']
            
            generate_pdf = options.pdf
            render(library, docname, data, realpath, out_dir, generate_pdf)


def render(library, docname, data, realpath, out_dir, generate_pdf):
    out = os.path.join(out_dir, docname + '.html')
    html_contents = render_complete(library=library,
                                    s=data, raise_errors=True, realpath=realpath,
                                    generate_pdf=generate_pdf)

    html_contents = embed_images_from_library(html=html_contents, library=library)

    doc = get_minimal_document(html_contents, add_markdown_css=True)

    with open(out, 'w') as f:
        f.write(doc)

    logger.info('Written %s ' % out)


mcdp_render_main = Render.get_sys_main()
