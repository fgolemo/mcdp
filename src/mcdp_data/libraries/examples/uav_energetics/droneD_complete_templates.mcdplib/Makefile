clean:
	@echo "Cleaning"


paper: paper-approxs paper-unc2 paper-unc3

paper-approxs:
	python plot_approximations.py

paper-unc2:
	python drone_unc2.py -c parmake

paper-unc3:
	python drone_unc3.py -c parmake

all: paper
	# mcdp-solve --cache -D ../../ -d . --out out --lower 5 test1  '<5 km, 600 [], 100 g>'
	#mcdp-solve -D ../../ -d . --out out --lower 15  test1  '<5 km, 600 [], 100 g>'
	
	# ok
	# mcdp-solve -D ../../ -d . --out out --upper 100  test1  '<5 km, 600 [], 100 g>'
	mcdp-solve -D ../../ -d . --out out --upper 100  test2  '<5 km, 600 [], 100 g>'

plots: plot1 plot3 plot1f
	
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



solve3:
	mcdp-solve --cache -D ../../ -d . --out out --upper 100 test3  '<5 km, 600 [], 100 g>'



solve2imp:
	mcdp-solve --cache -D ../../ -d . --out out --upper 100 --imp test2   '<5 km, 600 [], 100 g>'


solve3imp:
	mcdp-solve --cache -D ../../ -d . --out out --upper 100 --imp --make test3    '<5 km, 600 [], 100 g>'

figures:
	python drone_uncertain.py