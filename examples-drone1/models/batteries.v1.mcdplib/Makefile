all:
	./generate_batteries.py
	
	mcdp-solve --out out --imp batteries "<0.5 MJ, 1000 []>"
	
	python plot_batteries.py
	mcdp-plot --out out/plots Battery_NiCad
	mcdp-plot --out out/plots batteries_squash 
	
clean:
	rm -rf out-memo_disk out _cached
	rm -f bat_*.mcdp batteries.mcdp summary.txt
 
