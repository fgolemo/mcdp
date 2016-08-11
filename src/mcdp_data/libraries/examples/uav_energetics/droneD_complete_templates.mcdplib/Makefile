

all:
	# mcdp-solve --cache -D ../../ -d . --out out --lower 5 test1  '<5 km, 600 [], 100 g>'
	#mcdp-solve -D ../../ -d . --out out --lower 15  test1  '<5 km, 600 [], 100 g>'
	
	# ok
	# mcdp-solve -D ../../ -d . --out out --upper 100  test1  '<5 km, 600 [], 100 g>'
	mcdp-solve -D ../../ -d . --out out --upper 100  test2  '<5 km, 600 [], 100 g>'


plot:
	mcdp-plot --cache -D ../../ -d . --out out/plot_test1 test1 