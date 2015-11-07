all: plots solve

dp1=catalogue1.mcdp
dp2=catalogue_plus_coproduct.mcdp
dp3=catalogue_plus_coproduct-compact.mcdp
dp4=sizes.mcdp
outp=--out out/

clean:
	rm -rf out/
	
plots: plot1 plot2 plot3 plot4

plot1:
	mcdp-plot $(outp) choose.mcdp
	mcdp-plot $(outp) $(dp1)

plot2:
	mcdp-plot $(outp) $(dp2)

plot3:
	mcdp-plot $(outp) $(dp3)

plot4:
	mcdp-plot $(outp) $(dp4)

solve:
	mcdp-solve --plot $(outp) --expect_nres 2 --expect_nimp 2 $(dp2) "{1.5V}" "1 MJ"
	mcdp-solve --plot $(outp) --expect_nres 3 --expect_nimp 3 $(dp2) "{5V}" "1 MJ"


solve3:
	mcdp-solve --plot $(outp) --expect_nres 2 --expect_nimp 2 $(dp3) "{1.5V}" "1 MJ"
	mcdp-solve --plot $(outp) --expect_nres 3 --expect_nimp 3 $(dp3) "{5V}" "1 MJ"
