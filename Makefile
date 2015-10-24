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

comptests-run-parallel-nocontracts:
	mkdir -p $(out)
	DISABLE_CONTRACTS=1 comptests -o $(out) --nonose -c "rparmake" mocdp  

comptests-run-parallel-nocontracts-cov:
	mkdir -p $(out)
	DISABLE_CONTRACTS=1 comptests -o $(out) --coverage --nonose -c "rparmake" mocdp  


clean:
	rm -rf $(out)