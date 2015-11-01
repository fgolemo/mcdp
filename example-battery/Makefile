all: plots solve


solve:
	mcdp-solve battery.mcdp "1 hour" "0 kg" "0 W"
	mcdp-solve battery.mcdp "1 hour" "0.1 kg" "14 W" # feasible!
	mcdp-solve battery.mcdp "1 hour" "0.1 kg" "15 W" # unfeasible
	mcdp-solve battery.mcdp "1 hour" "0.12 kg" "14 W"

plots:
	mcdp-plot battery_compact.mcdp 
	mcdp-plot battery.mcdp 