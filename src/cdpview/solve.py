from quickapp.quick_app_base import QuickAppBase
import os
from mocdp.lang.parse_actions import parse_wrap, parse_ndp
from mocdp.lang.syntax import Syntax
from mocdp.dp.solver import generic_solve
from mocdp.posets.uppersets import UpperSets
from mocdp.posets.poset_product import PosetProduct
from mocdp.posets.types_universe import get_types_universe
from mocdp.comp.context import Context
from mocdp.lang.blocks import eval_constant
from conf_tools.global_config import GlobalConfig


class SolveDP(QuickAppBase):
    """ Plot a design program """
    def define_program_options(self, params):
#         params.add_string('filename')
#         params.add_flag('watch')
        params.add_string('out', help='Output dir', default=None)
#         params.add_string_list('plots', default='*')
        params.accept_extra()

    def go(self):
        GlobalConfig.global_load_dir("mocdp")

        options = self.get_options()
#         filename = options.filename
        params = options.get_extra()

        if len(params) < 1:
            raise ValueError('Please specify filename.')

        filename = params[0]

        if options.out is None:
            out = os.path.dirname(filename)
            if not out:
                out = '.'
        else:
            out = options.out


        params = params[1:]



        fd = []
        Fd = []
        context = Context()
        for p in params:
            res = parse_wrap(Syntax.number_with_unit, p)[0]
            vu = eval_constant(res, context)
            fd.append(vu.value)
            Fd.append(vu.unit)
        Fd = PosetProduct(Fd)
        fd = tuple(fd)

        s = open(filename).read()
        ndp = parse_ndp(s)
        dp = ndp.get_dp()

        F = dp.get_fun_space()

        # TODO: check units compatible

        tu = get_types_universe()

        tu.check_leq(Fd, F)

        f = fd
        try: 
            trace = generic_solve(dp, f=f, max_steps=None)
            print('Iteration result: %s' % trace.result)
            ss = trace.get_s_sequence()
            S = trace.S
            print('Fixed-point iteration converged to: %s' % S.format(ss[-1]))
            R = trace.dp.get_res_space()
            UR = UpperSets(R)
            sr = trace.get_r_sequence()
            rnames = ndp.get_rnames()
            x = ", ".join(rnames)
            print('Minimal resources needed: %s = %s' % (x, UR.format(sr[-1])))

        except:
            raise
            pass
#
#         plots = expand_string(options.plots, list(allplots))
#         do_plots(filename, plots, out)
#
#         if options.watch:
#             def handler():
#                 do_plots(filename, plots, out)
#
#             from cdpview.go import watch
#             watch(path=os.path.dirname(options.filename), handler=handler)


mcdp_solve_main = SolveDP.get_sys_main()
