from comptests.registrar import comptest, comptest_fails
from mcdp_lang.parse_interface import parse_poset

@comptest_fails
def check_lang_multiset1():
    P = parse_poset('multiset( finite_poset {a b c d e })')


@comptest
def check_lang_multiset2():
    #     eval_rvalue_as_constant("Bot set-of(V)")
    pass

@comptest
def check_lang_multiset3():
    pass


@comptest
def check_lang_multiset4():
    pass

@comptest
def check_lang_multiset5():
    pass


@comptest
def check_lang_multiset6():
    pass


@comptest
def check_lang_multiset7():
    pass

