from mcdp_report.my_gvgen import GvGen
from mcdp_report.gg_ndp import GraphDrawingContext

gg = GvGen()
gdc = GraphDrawingContext(gg, parent=None, yourname='root')
l0  = gdc.newItem('l0')

C = gdc.newItem('C')

with gdc.child_context_yield(l0, "l0") as gdc2:
    l1 = gdc2.newItem('l1')

    with gdc2.child_context_yield(l1, "l1") as gdc3:
        gdc3.newItem('l2a')
        gdc3.newItem('l2b')
        l2c = gdc3.newItem('l2c')

        with gdc2.child_context_yield(l2c, "l2c") as gdc4:
            gdc4.newItem('A')
            B = gdc4.newItem('B')

gdc.newLink(C, B)

# gg.dot()

print gg.dot2()
