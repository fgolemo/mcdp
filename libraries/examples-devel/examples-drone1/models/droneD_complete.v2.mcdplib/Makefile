all:
	
	mcdp-plot --out=out -d . DroneComplete
	mcdp-plot --out=out -d . market

clean:
	rm -rf out _cached out-memo_disk


bug:
	rm -f _cached/market*.cached
	mcdp-plot --out=out -d . market_flatten
bug2:
	rm -f _cached/test*.cached
	mcdp-plot --out=out -d . test