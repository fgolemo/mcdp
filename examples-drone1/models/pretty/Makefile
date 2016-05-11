all:
	mcdp-plot --out out -d ../batteries.v1.mcdplib:. battery_squash
	mcdp-plot --out out battery_replacement
	mcdp-plot --out out battery_catalogue
	mcdp-plot --out out actuation1
	mcdp-plot --out out actuation2

	mcdp-plot --out out battery

clean:
	rm -rf out _cached
