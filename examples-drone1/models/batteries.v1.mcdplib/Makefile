all:

	./generate_batteries.py
	rm -rf out-memo_disk
	
	mcdp-solve --out out --imp batteries "<0.5 MJ, 1000 []>"
	
	python plot_batteries.py
	mcdp-plot --out out/plots bat_NiCad
	mcdp-plot --out out/plots batteries_squash 