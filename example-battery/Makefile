all: plots solve


solve:
	mcdp_solve battery.mcdp "1 hour" "0 kg" "0 W"
	mcdp_solve battery.mcdp "1 hour" "0.2 kg" "0 W"
	mcdp_solve battery.mcdp "1 hour" "0.2 kg" "10 W"

plots:
	mcdp_plot --filename battery_compact.mcdp 
	mcdp_plot --filename battery.mcdp 