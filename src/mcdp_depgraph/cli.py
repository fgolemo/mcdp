# -*- coding: utf-8 -*-
from mcdp_depgraph.draw_dep_graph import draw_depgraph
from mcdp_depgraph.find_dep import find_dependencies
from quickapp import QuickApp
import logging
from mcdp_depgraph.other_reports import other_jobs


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
            raise ValueError('Please specify model name.')

        config_dirs = options.config_dirs.split(":")
        maindir = options.maindir
        seeds = params
        res = context.comp(find_dependencies, config_dirs=config_dirs,
                           maindir=maindir, seeds=seeds)

        print('config_dirs: {}'.format(config_dirs))
        print('maindir: {}'.format(maindir))

        context.comp_dynamic(other_jobs, maindir=maindir, config_dirs=config_dirs,
                             outdir=options.output, res=res)

        r = context.comp(draw_depgraph, res)
        context.add_report(r, 'draw')

            
            
mcdp_depgraph_main = Depgraph.get_sys_main()









