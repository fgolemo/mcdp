# -*- coding: utf-8 -*-

#                                                                    
# > | Exception: connect2() failed                                                                                           
# > |      ndp2: Instance of <class 'mocdp.comp.wrap.SimpleWrap'>.                                                           
# > |            Wrap(['a', 'b']|Multiply(R[s]×R[W]→R[J])|['res'])                                                        
# > | connections: Instance of <type 'set'>.                                                                                 
# > |              set([Connection(dp1='group2', s1='actuation_power', dp2='mult1', s2='b')])                                
# > |      ndp1: Instance of <class 'mocdp.comp.wrap.SimpleWrap'>.                                                           
# > |            Wrap(['extra_payload', 'p0']|Series(Series(Series(Series(Parallel(Id(R[g]), Id(R[g])), Mux(R[g]×R[g] → R[g]×R[g], [(1,), (0,)])), Sum(R[g])), Mux(R[g] → R[g], ())), Mobility(R[g]→R[W]))|['actuation_power'])
# > |     split: Instance of <type 'set'>.                                                                                   
# > |            set([])                                                               

from comptests.registrar import comptest
from mocdp.posets.rcomp import Rcomp
from mocdp.dp.primitive import PrimitiveDP
from mocdp.comp.wrap import SimpleWrap
from mocdp.comp.connection import Connection, connect2

def get_dummy(fnames, rnames):
    
    base = (Rcomp,)
    F = base * len(fnames)
    R = base * len(rnames)
    
    class Dummy(PrimitiveDP):
        def __init__(self):
            PrimitiveDP.__init__(self, F=F, R=R)
        def solve(self, _func):
            return self.R.bottom()
    return SimpleWrap(Dummy(), fnames, rnames)
    
@comptest
def check_connect2():
    # 
    #  f0 -> |  | -----> r0
    #  f1 -> |c1| -----> r1
    #  f2 -> |  | -r2:F0-> | c2 | -> R0
    #  F1----------------> |    | -> R1
    
    
    ndp1 = get_dummy(['f0', 'f1', 'f2'], ['r0, r1, r2'])
    ndp1 = get_dummy(['F0', 'F1'], ['R0', 'R1'])
    
    connections = Connection('-', 'r2', '-', 'F0')

    res = connect2(ndp1, ndp1, connections, split=set())
