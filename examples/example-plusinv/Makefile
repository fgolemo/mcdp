all: plots solve 

outp=--out out/
dp1=plusinv1
dp2=plusinv2
dp3=plusinv3
dp4=plusinv4
dp5=plusinv5
dp6=plusinvnat1
dp7=plusinvnat2

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
	