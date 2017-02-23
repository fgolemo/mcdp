all: plots solve 


dp1=battery

clean:
	rm -rf out/

solve:
	mcdp-solve  --out out/01 $(dp1) "<1 hour, 0 kg, 0 W>"
	mcdp-solve  --out out/02 $(dp1) "<1 hour, 0.1 kg, 14 W>" # feasible!
	mcdp-solve  --out out/03 $(dp1) "<1 hour, 0.1 kg, 15 W>" # unfeasible
	mcdp-solve  --out out/01 $(dp1) "<1 hour, 0.12 kg, 14 W>"

# solve_old_syntax:
# 	mcdp-solve  $(outp) $(dp1) "1 hour" "0 kg" "0 W"

plots:
	mcdp-plot --out out/visualization $(dp1)
	mcdp-plot --out out/visualization battery_compact
	mcdp-plot --out out/visualization battery_minimal
	