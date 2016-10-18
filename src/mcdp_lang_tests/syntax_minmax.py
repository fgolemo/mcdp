# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from contracts.utils import check_isinstance
from mcdp_dp import JoinNDP, MeetNDP, MeetNDualDP, JoinNDualDP
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parse_interface import parse_ndp
from mcdp_lang.syntax import Syntax


@comptest
def check_minmax1(): # TODO: rename
    ndp = parse_ndp("""
        mcdp {
            provides f1 [Nat]
            provides f2 [Nat]
            requires r [Nat]
            
            max(provided f1, provided f2) <= required r
        }
    """)
    dp = ndp.get_dp()
    check_isinstance(dp, JoinNDP)

@comptest
def check_minmax2(): # TODO: rename
    ndp = parse_ndp("""
        mcdp {
            provides f1 [Nat]
            provides f2 [Nat]
            requires r  [Nat]
            
            min(provided f1, provided f2) <= required r
        }
    """)
    dp = ndp.get_dp()
    check_isinstance(dp, MeetNDP)

@comptest
def check_minmax3(): # TODO: rename
    
    parse_wrap(Syntax.opname_f, 'min')
    parse_wrap(Syntax.fvalue_binary, 'min(required r1, required r2)')
    parse_wrap(Syntax.fvalue, 'min(required r1, required r2)')

    ndp = parse_ndp("""
        mcdp {
            provides f [Nat]
    
            requires r1 [Nat]
            requires r2 [Nat]
            
            provided f <= min(required r1, required r2)
        }
    """)
    dp = ndp.get_dp()
    check_isinstance(dp, MeetNDualDP)


@comptest
def check_minmax4(): # TODO: rename
    ndp = parse_ndp("""
        mcdp {
            provides f [Nat]
    
            requires r1 [Nat]
            requires r2 [Nat]
            
            provided f <= max(required r1, required r2)
        }
    """)
    dp = ndp.get_dp()
    check_isinstance(dp, JoinNDualDP)