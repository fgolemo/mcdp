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
