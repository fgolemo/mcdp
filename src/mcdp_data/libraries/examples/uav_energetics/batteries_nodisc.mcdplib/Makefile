all:
	./generate_batteries.py
	
	mcdp-solve --out out --imp batteries "<0.5 MJ, 1000 []>"
	
	./plot_batteries.py

	mcdp-plot --out out Battery_NiCad
	mcdp-plot --out out batteries_squash 
	mcdp-plot --out out batteries

	
clean:
	rm -rf out-memo_disk out _cached
	rm -f bat_*.mcdp batteries.mcdp summary.txt
 

solve2:
	mcdp-solve --out out --plot --imp Battery_NiCad  "<0.6 MJ, 1000 []>"
