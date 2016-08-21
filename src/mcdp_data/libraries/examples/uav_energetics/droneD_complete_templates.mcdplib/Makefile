all: paper-figures

clean:
	@echo "Cleaning"
	rm -rf out-drone*
	rm -rf out-plot_approximations
	rm -rf _cached

paper-figures: paper-approxs paper-unc1 paper-unc2 paper-unc3

paper-approxs:
	python plot_approximations.py

paper-unc1:
	python drone_unc1.py -c parmake

paper-unc2:
	python drone_unc2.py -c parmake

paper-unc3:
	python drone_unc3.py -c parmake

	 
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
