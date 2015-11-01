from conf_tools import GlobalConfig
from contracts.utils import raise_desc
from mocdp.comp.context import Context
from mocdp.dp.solver import generic_solve
from mocdp.dp.tests.inv_mult_plots import generic_report
from mocdp.lang.blocks import eval_constant
from mocdp.lang.parse_actions import parse_ndp, parse_wrap
from mocdp.lang.syntax import Syntax
from mocdp.posets import PosetProduct, UpperSets, get_types_universe
from quickapp import QuickAppBase
from reprep import Report
import os


class SolveDP(QuickAppBase):
    """ Plot a design program """
    def define_program_options(self, params):
        params.add_string('out', help='Output dir', default=None)
        params.add_int('max_steps', help='Maximum number of steps', default=None)
        params.accept_extra()
        params.add_flag('plot', help='Show iterations graphically')
        params.add_flag('imp', help='Show implementations')

    def go(self):
        GlobalConfig.global_load_dir("mocdp")

        options = self.get_options()
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

        fnames = ndp.get_fnames()
        if len(fnames) != len(fd):
            raise_desc(ValueError, 'Length does not match.', fnames=fnames,
                       params=params)

        if len(fnames) == 1:
            Fd = Fd[0]
            fd = fd[0]
        else:
            Fd = Fd
            fd = fd


        F = dp.get_fun_space()

        # TODO: check units compatible

        tu = get_types_universe()

        tu.check_leq(Fd, F)

        A_to_B, _ = tu.get_embedding(Fd, F)
        fg = A_to_B(fd)

        print('query: %s' % ", ".join(params))
        print('converted: %s' % F.format(fg))
        max_steps = options.max_steps
        try: 
            trace = generic_solve(dp, f=fg, max_steps=max_steps)
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

        if options.imp:
            M = dp.get_imp_space_mod_res()
            for r in sr[-1].minimals:
                ms = dp.get_implementations_f_r(f=fg, r=r)
                s = 'r = %s ' % R.format(r)
                for m in ms:
                    s += "m = %s " % M.format(m)
                print(s)

        if options.plot:
            r = Report()
            generic_report(r, dp, trace, annotation=None, axis0=(0, 0, 0, 0))
            out_html = os.path.splitext(filename)[0] + '-solve.html'
            print('writing to %r' % out_html)
            r.to_html(out_html)
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
