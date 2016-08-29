all: paper-figures

clean:
	@echo "Cleaning"
	rm -rf out-drone*
	rm -rf out-plot_approximations
	rm -rf _cached
	rm -rf generated

paper-figures: paper-approxs paper-unc1 paper-unc2 paper-unc3

paper-approxs:
	python plot_approximations.py

paper-unc1:
	python drone_unc1.py -c parmake

paper-unc2:
	python drone_unc2.py -c parmake

paper-unc3:
	python drone_unc3.py -c parmake

used = \
	drone_unc1_batteries_uncertain1 \
	drone_unc1_batteries_uncertain2 \
	drone_unc1_batteries_uncertain3 \
	drone_unc2_00_0_mw\
	drone_unc2_01_0_01_mw \
	drone_unc2_02_0_1_mw\
	drone_unc2_03_1_0_mw \
	drone_unc2_04_5_0_mw\
	drone_unc2_05_10_0_mw\
	drone_unc2_06_50_mw\
	drone_unc2_07_100_0_mw\
	drone_unc2_08_250_mw\
	drone_unc2_09_500_mw\
	drone_unc2_10_1000_mw\
	drone_unc3


depgraph:
	mcdp-depgraph --contracts -D ../.. -d . -c 'remake all; rmake' $(used)

	 
plot1:
	#rm -rf out/plot_test1
	mcdp-plot --cache -D ../../ -d . --out out/plot_test1 test1 

plot1f:
	#rm -rf out/plot_test1
	mcdp-plot --cache -D ../../ -d . --out out/plot_test1_flatten test1_flatten 

#plot2:
#	mcdp-plot --cache -D ../../ -d . --out out/plot_test1 --plots dp_graph_tree,dp_graph_flow test2

plot3:
	#mcdp-plot --cache -D ../../ -d . --out out/plot_test1 --plots dp_graph_tree,dp_graph_tree_compact test3
	mcdp-plot --cache -D ../../ -d . --out out/plot_test1 --plots ndp_greenredsym test3 

plot4: 

	mcdp-plot --cache -D ../../ -d . --out out/plot_test4 --plots ndp_greenredsym test4 

solve3:
	mcdp-solve --cache -D ../../ -d . --out out --upper 100 test3  '<5 km, 600 [], 100 g>'


solve2imp:
	mcdp-solve --cache -D ../../ -d . --out out --upper 100 --imp test2   '<5 km, 600 [], 100 g>'


solve3imp:
	mcdp-solve --cache -D ../../ -d . --out out --upper 100 --imp --make test3    '<5 km, 600 [], 100 g>'
