all: plots solve

plots:
	mcdp-plot catalogue2.mcdp

solve:
	mcdp-solve catalogue2.mcdp	"{1.5 V}" "1 J"
	mcdp-solve --expect_nres 2 --expect_nimp 2 --imp catalogue_plus_coproduct.mcdp "{1.5V}" "1 MJ"

go:
	mcdp-plot catalogue1.mcdp

