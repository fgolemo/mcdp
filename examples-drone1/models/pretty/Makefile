all:
	mcdp-plot --out out --plots syntax_pdf batteries
	mcdp-plot --out out --plots syntax_pdf ae1

	mcdp-plot --out out --plots syntax_pdf -d ../batteries.v1.mcdplib:. battery_squash
	mcdp-plot --out out --plots syntax_pdf battery_replacement
	mcdp-plot --out out --plots syntax_pdf battery_catalogue
	mcdp-plot --out out --plots syntax_pdf actuation1
	mcdp-plot --out out --plots syntax_pdf actuation2

	mcdp-plot --out out --plots syntax_pdf battery

clean:
	rm -rf out _cached
