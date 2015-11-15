all: plots solve solve_old_syntax

outp=--out out/
dp1=plusinv1.mcdp
dp2=plusinv2.mcdp
dp3=plusinv3.mcdp
dp4=plusinv4.mcdp

clean:
	rm -rf out/

solve:
	mcdp-solve  $(outp) $(dp1)
	mcdp-solve   $(outp) $(dp2) 
	mcdp-solve   $(outp) $(dp3) 
	mcdp-solve   $(outp) $(dp4) 

plots:
	mcdp-plot $(outp) $(dp1) 
	mcdp-plot $(outp) $(dp2) 
	mcdp-plot $(outp) $(dp3) 
	mcdp-plot $(outp) $(dp4) 
	