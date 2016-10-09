# -*- coding: utf-8 -*-
from contracts.enabling import disable_all
from mcdp_library.libraries import Librarian
from quickapp import QuickAppBase
import logging
import os


class Eval(QuickAppBase):
    """ Evaluates one of the constants """

    def define_program_options(self, params):
        params.add_string('out', help='Output dir', default=None)

        params.accept_extra()
        params.add_flag('cache')
        params.add_flag('contracts')

        params.add_string('config_dirs', default='.', short='-D',
                           help='Other libraries.')
        params.add_string('maindir', default='.', short='-d',
                           help='Library directories containing models, separated by :.')

    def go(self):
        from mocdp import logger
        logger.setLevel(logging.DEBUG)



        options = self.get_options()

        if not options.contracts:
            disable_all()

        params = options.get_extra()

        if len(params) < 1:
            raise ValueError('Please specify name.')

        name = params[0]

        config_dirs = options.config_dirs.split(":")
        maindir = options.maindir
        out_dir = options.out

        if out_dir is None:
            out_dir = os.path.join('out', 'mcdp_eval')

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

        library.load_constant(name)

mcdp_eval_main = Eval.get_sys_main()
