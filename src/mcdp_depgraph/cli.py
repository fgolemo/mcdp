# -*- coding: utf-8 -*-
import logging

from quickapp import QuickApp

from .draw_dep_graph import draw_depgraph, draw_libdepgraph
from .find_dep import find_dependencies
from .other_reports import other_jobs


class Depgraph(QuickApp):
    """ Solves an MCDP. """

    def define_options(self, params):

        params.add_string('config_dirs', default='.', short='-D',
                           help='Other libraries, separated by :')
        params.add_string('maindir', default='.', short='-d',
                           help='Library directories containing models')

        params.accept_extra()
        #         params.add_flag('cache')

    def define_jobs_context(self, context):
        from mocdp import logger
        logger.setLevel(logging.DEBUG)

        options = self.get_options()
        params = options.get_extra()

        if len(params) < 1:
            seeds = None
            #raise ValueError('Please specify some model names to be used as seeds.')
        else:
            seeds = params

        config_dirs = options.config_dirs.split(":")
        maindir = options.maindir
        res = context.comp(find_dependencies, config_dirs=config_dirs,
                           maindir=maindir, seeds=seeds)

        print('config_dirs: {}'.format(config_dirs))
        print('maindir: {}'.format(maindir))

        context.comp_dynamic(other_jobs, maindir=maindir, config_dirs=config_dirs,
                             outdir=options.output, res=res)

        r = context.comp(draw_depgraph, res)
        context.add_report(r, 'draw')

        r = context.comp(draw_libdepgraph, res)
        context.add_report(r, 'libdepgraph')

            
            
mcdp_depgraph_main = Depgraph.get_sys_main()









