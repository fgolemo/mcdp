package=mocdp

include pypackage.mk

out=out/comptests

comptests:
	mkdir -p $(out)
	comptests -o $(out) --contracts --nonose --console mocdp

comptests-run:
	mkdir -p $(out)
	comptests -o $(out) --contracts --nonose mocdp 

comptests-run-parallel:
	mkdir -p $(out)
	comptests -o $(out) --contracts --nonose -c "rparmake" mocdp  


clean:
	rm -rf $(out)