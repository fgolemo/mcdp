all: plots solve


solve:
	mcdp-solve battery.mcdp "1 hour" "0 kg" "0 W"
	mcdp-solve battery.mcdp "1 hour" "0.2 kg" "0 W"
	mcdp-solve battery.mcdp "1 hour" "0.2 kg" "10 W"

plots:
	mcdp-plot battery_compact.mcdp 
	mcdp-plot battery.mcdp 