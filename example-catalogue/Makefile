all: plots solve

dp1=catalogue_plus_coproduct.mcdp

plots:
	mcdp-plot $(dp1)

solve:
	mcdp-solve --plot --out out --expect_nres 2 --expect_nimp 2 $(dp1) "{1.5V}" "1 MJ"
	mcdp-solve --plot --out out --expect_nres 3 --expect_nimp 3 $(dp1) "{5V}" "1 MJ"

