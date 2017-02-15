# -*- coding: utf-8 -*-
import logging
import os

from decent_params import UserError
from mcdp import logger
from quickapp import QuickAppBase

from .solve_meat import solve_main
from contracts.enabling import disable_all


class SolveDP(QuickAppBase):
    """ Solves an MCDP. """

    def define_program_options(self, params):
        params.add_string('out',
                          help='Output dir', default=None)
        params.add_int('max_steps',
                       help='Maximum number of steps', default=None)

        params.add_int('expect_nimp',
                       help='Expected number of implementations.',
                        default=None)
        params.add_int('expect_nres',
                       help='Expected number of resources.',
                        default=None)
        params.accept_extra()
        params.add_flag('cache')
        params.add_flag('plot', 
                        help='Show iterations graphically')
        params.add_flag('movie', 
                        help='Create animation.')
        params.add_flag('imp', 
                        help='Compute and show implementations.')
        params.add_flag('make', 
                        help='Runs the make procedure on the implementations.')

        params.add_string('config_dirs', default='.', short='-D',
                           help='Other libraries.')
        params.add_string('maindir', default='.', short='-d',
                           help='Library directories containing models, '
                           'separated by :.')

        params.add_flag('advanced',
                        help='Solve by advanced solver (in development)')
        params.add_flag('intervals',
                        help='Use intervals')
        params.add_int('lower', default=None,
                       help='Use lower bound approx')
        params.add_int('upper', default=None,
                       help='Use upper bound approx')
        
        params.add_flag('contracts', 
                        help='Activate contracts.')


    def go(self):
        
        logger.setLevel(logging.DEBUG)

        options = self.get_options()
        
        if not options.contracts:
            logger.debug('Disabling PyContrats. Use --contracts to enable.')
            disable_all()
            
        if options.expect_nimp is not None:
            options.imp = True

        params = options.get_extra()

        if len(params) < 1:
            raise ValueError('Please specify model name.')

        model_name = params[0]

        # drop the extension
        if '.mcdp' in model_name or '/' in model_name:
            msg = 'The model name should not contain extension or /.'
            raise UserError(msg)

        max_steps = options.max_steps

        _exp_advanced = options.advanced
        expect_nres = options.expect_nres
        lower = options.lower
        upper = options.upper
        out_dir = options.out
        query_strings = params[1:]

        intervals = options.intervals
        imp = options.imp
        expect_nimp = options.expect_nimp
        make = options.make
        if make: imp = True

        plot = options.plot
        do_movie = options.movie

        expect_res = None

        config_dirs = options.config_dirs.split(":")
        maindir = options.maindir
        if options.cache:
            if out_dir is None:
                out_dir = 'out-mcdp_solve'
            cache_dir = os.path.join(out_dir, '_cached', 'solve')
        else:
            cache_dir = None

        solve_main(logger, config_dirs, maindir, cache_dir, model_name, lower, upper, out_dir, max_steps, query_strings,
                   intervals, _exp_advanced, expect_nres, imp, expect_nimp, plot, do_movie,
                   expect_res,
                   make)

mcdp_solve_main = SolveDP.get_sys_main()
