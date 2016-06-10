
basic-remake:
	compmake out/comptests -c "remake mcdplib-basic-*setup*; make mcdplib-basic-poset-*"

out=out/comptests

package=mocdp

comptests:
	mkdir -p $(out)
	comptests -o $(out) --contracts --nonose --console $(package)

comptests-nocontracts:
	mkdir -p $(out)
	comptests -o $(out) --nonose --console $(package)

comptests-run:
	mkdir -p $(out)
	comptests -o $(out) --contracts --nonose $(package) 

comptests-run-nocontracts:
	mkdir -p $(out)
	comptests -o $(out) --nonose $(package) 

comptests-run-nocontracts-console:
	mkdir -p $(out)
	comptests -o $(out) --nonose $(package) --console

comptests-run-parallel:
	mkdir -p $(out)
	comptests -o $(out) --contracts --nonose -c "rparmake" $(package)  

comptests-run-parallel-nocontracts:
	mkdir -p $(out)
	DISABLE_CONTRACTS=1 comptests -o $(out) --nonose -c "rparmake" $(package)  

comptests-run-parallel-nocontracts-cov:
	mkdir -p $(out)
	DISABLE_CONTRACTS=1 comptests -o $(out) --coverage --nonose -c "rparmake" $(package)  

comptests-run-parallel-nocontracts-prof:
	mkdir -p $(out)
	DISABLE_CONTRACTS=1 comptests -o $(out) --profile --nonose -c "make; rparmake not *testlang13diagram*" $(package)  

clean:
	rm -rf $(out) _cached


stats-locs:
	wc -l `find . -type f -name '*.py' | grep -v test`

stats-locs-tests:
	wc -l `find . -type f -name '*.py' | grep test`

