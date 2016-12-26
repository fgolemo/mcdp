# -*- coding: utf-8 -*-
import logging
import os

from contracts.enabling import disable_all
from contracts.utils import raise_desc
from decent_params import UserError
from mcdp_library import Librarian, MCDPLibrary
from mcdp_web.renderdoc.highlight import get_minimal_document
from mcdp_web.renderdoc.main import render_complete
from mocdp import logger
from quickapp import QuickAppBase


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
            suffix =  '.' + MCDPLibrary.ext_doc_md
            if docname.endswith(suffix):
                docname = docname.replace(suffix,'')
            basename = docname + suffix
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

    title = docname
    doc = get_minimal_document(html_contents, title=title,
                               add_markdown_css=True, add_manual_css=True)

#     from mcdp_docs.check_missing_links import check_if_any_href_is_invalid
#     soup = bs(doc)
#     check_if_any_href_is_invalid(doc)
#     
    
    d = os.path.dirname(out)
    if not os.path.exists(d):
        os.makedirs(d)
    with open(out, 'w') as f:
        f.write(doc)

    logger.info('Written %s ' % out)


mcdp_render_main = Render.get_sys_main()
