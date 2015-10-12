package=mocdp

include pypackage.mk

out=out/comptests

comptests:
	mkdir -p $(out)
	comptests -o $(out) --contracts --console mocdp

comptests-run:
	mkdir -p $(out)
	comptests -o $(out) --contracts --nonose mocdp 


clean:
	rm -rf $(out)