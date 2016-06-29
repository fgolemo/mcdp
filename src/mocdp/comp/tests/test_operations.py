from mcdp_tests.generation import for_all_nameddps
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.wrap import SimpleWrap


@for_all_nameddps
def check_abstraction(_, ndp):
    ndp2 = ndp.abstract()
    assert isinstance(ndp2, SimpleWrap)
    check_same_interface(ndp, ndp2)
    
@for_all_nameddps
def check_compact(_, ndp):
    ndp2 = ndp.compact()
    check_same_interface(ndp, ndp2)

@for_all_nameddps
def check_templatize_children(_, ndp):
    if not isinstance(ndp, CompositeNamedDP):
        return
    ndp.templatize_children()

@for_all_nameddps
def check_makecanonical(_, ndp):
    # TODO: just return itself?
    if not isinstance(ndp, CompositeNamedDP):
        return

    from mocdp.comp.composite_makecanonical import cndp_makecanonical
    ndp2 = cndp_makecanonical(ndp)
    check_same_interface(ndp, ndp2)


def check_same_interface(ndp, ndp2):
    assert ndp.get_fnames() == ndp2.get_fnames(), (ndp.get_fnames(), ndp2.get_fnames())
    assert ndp.get_rnames() == ndp2.get_rnames(), (ndp.get_rnames(), ndp2.get_rnames())
    assert ndp.get_ftypes() == ndp2.get_ftypes(), (ndp.get_ftypes(), ndp2.get_ftypes())
    assert ndp.get_rtypes() == ndp2.get_rtypes(), (ndp.get_rtypes(), ndp2.get_rtypes())
    
