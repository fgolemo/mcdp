all: plots solve 

outp=--out out/
dp1=plusinv1.mcdp
dp2=plusinv2.mcdp
dp3=plusinv3.mcdp
dp4=plusinv4.mcdp
dp5=plusinv5.mcdp
dp6=plusinvnat1.mcdp
dp7=plusinvnat2.mcdp

clean:
	rm -rf out/

solve:
	mcdp-solve  --plot $(outp) $(dp1)  "10 s"
	mcdp-solve  --plot $(outp) $(dp2)  "10 s"
	mcdp-solve  --plot $(outp) $(dp3) 	"10 s"
	mcdp-solve  --plot $(outp) $(dp4)  "10 s"
	mcdp-solve  --plot $(outp) $(dp5)  "nat:5"
	mcdp-solve  --plot $(outp) $(dp6)  "nat:4"
	mcdp-solve  --plot $(outp) $(dp7)  "nat:4"
	

plots:
	mcdp-plot $(outp) $(dp1) 
	mcdp-plot $(outp) $(dp2) 
	mcdp-plot $(outp) $(dp3) 
	mcdp-plot $(outp) $(dp4) 
	mcdp-plot $(outp) $(dp5) 
	mcdp-plot $(outp) $(dp6) 
	mcdp-plot $(outp) $(dp7) 
	