
all:
	./plot_batteries_choice.py  -c rparmake
	./plot_drone.py  -c rparmake

clean:
	rm -rf out-plot_batteries_choice.py


pics: pics1 pics2 pics3


pics3: 
	mcdp-plot -D .. --out out/batteries2_min_cost batteries2_min_cost

pics2: 
	mcdp-plot -D .. --out out/drone_pretty drone_pretty
	mcdp-plot -D .. --out out/actuation Actuation
	mcdp-plot -D .. --out out/drone1 drone1


pics1:
	mcdp-plot --out out/Battery_LCO Battery_LCO