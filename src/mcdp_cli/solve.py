# -*- coding: utf-8 -*-
from .solve_meat import solve_main
from decent_params import UserError
from quickapp import QuickAppBase
import logging


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
        params.add_flag('plot', help='Show iterations graphically')
        params.add_flag('movie', help='Create animation.')
        params.add_flag('imp', help='Compute and show implementations.')
        params.add_flag('make', help='Runs the make procedure on the implementations.')

        params.add_string('dirs', default='.', short='-d',
                           help='Library directories containing models, separated by :.')

        params.add_flag('advanced',
                        help='Solve by advanced solver (in development)')
        params.add_flag('intervals',
                        help='Use intervals')
        params.add_int('lower', default=None,
                       help='Use lower bound approx')
        params.add_int('upper', default=None,
                       help='Use upper bound approx')

    def go(self):
        from mocdp import logger
        logger.setLevel(logging.DEBUG)

        options = self.get_options()
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
        config_dirs = options.dirs.split(":")
        intervals = options.intervals
        imp = options.imp
        expect_nimp = options.expect_nimp
        make = options.make
        if make: imp = True

        plot = options.plot
        do_movie = options.movie

        expect_res = None

        solve_main(logger, config_dirs, model_name, lower, upper, out_dir, max_steps, query_strings,
                   intervals, _exp_advanced, expect_nres, imp, expect_nimp, plot, do_movie,
                   expect_res,
                   make)

mcdp_solve_main = SolveDP.get_sys_main()
