from comptests.registrar import comptest
from mcdp_dp.dp_sum import ProductNatN


@comptest
def check_product1():
    
    amap = ProductNatN(4)

    assert amap((1,3,4,5)) == 5*4*3