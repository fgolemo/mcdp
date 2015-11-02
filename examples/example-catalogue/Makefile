all: plots solve

dp1=catalogue1.mcdp
dp2=catalogue_plus_coproduct.mcdp
outp=--out out/

clean:
	rm -rf out/
	
plots:
	mcdp-plot $(outp) choose.mcdp
	mcdp-plot $(outp) $(dp1)
	mcdp-plot $(outp) $(dp2)

solve:
	mcdp-solve --plot $(outp) --expect_nres 2 --expect_nimp 2 $(dp2) "{1.5V}" "1 MJ"
	mcdp-solve --plot $(outp) --expect_nres 3 --expect_nimp 3 $(dp2) "{5V}" "1 MJ"

