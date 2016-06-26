from mcdp_tests.generation import for_all_nameddps


@for_all_nameddps
def check_abstraction(_, ndp):
    ndp.abstract()
    
@for_all_nameddps
def check_compact(_, ndp):
    ndp.compact()

@for_all_nameddps
def check_templatize_children(_, ndp):
    ndp.templatize_children()

@for_all_nameddps
def check_makecanonical(_, ndp):
    from mocdp.comp.composite_makecanonical import cndp_makecanonical
    ndp2 = cndp_makecanonical(ndp)

    assert ndp2.get_fnames() == ndp.get_fnames()
    assert ndp2.get_rnames() == ndp.get_rnames()
