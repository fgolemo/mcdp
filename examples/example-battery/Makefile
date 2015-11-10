all: plots solve solve_old_syntax

outp=--out out/
dp1=battery.mcdp

clean:
	rm -rf out/

solve:
	mcdp-solve  $(outp) $(dp1) "<1 hour, 0 kg, 0 W>"
	mcdp-solve   $(outp) $(dp1) "<1 hour, 0.1 kg, 14 W>" # feasible!
	mcdp-solve   $(outp) $(dp1) "<1 hour, 0.1 kg, 15 W>" # unfeasible
	mcdp-solve   $(outp) $(dp1) "<1 hour, 0.12 kg, 14 W>"

solve_old_syntax:
	mcdp-solve  $(outp) $(dp1) "1 hour" "0 kg" "0 W"

plots:
	mcdp-plot $(outp) $(dp1) 
	mcdp-plot $(outp) battery_compact.mcdp 
	