# -*- coding: utf-8 -*-
def get_ndp():
	from mcdp_lang import parse_ndp
	return parse_ndp("mcdp {}")

def get_poset():
	from mcdp_posets import Nat
	return Nat()
	
def get_primitivedp():
	from mcdp_dp import Identity
	from mcdp_posets import Nat
	return Identity(Nat())

	#mcdp_primitive