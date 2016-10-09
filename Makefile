
#basic-remake:
#	compmake out/comptests -c "remake mcdplib-basic-*setup*; make mcdplib-basic-poset-*"

out=out/comptests

package=mcdp_tests

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
	DISABLE_CONTRACTS=1 comptests -o $(out) --profile --nonose -c "make; rparmake" $(package)  


docoverage-single:
	# note you need "rmake" otherwise it will not be captured
	rm -rf ouf_coverage .coverage
	-DISABLE_CONTRACTS=1 comptests -o $(out) --nonose -c "exit" $(package)
	-DISABLE_CONTRACTS=1 coverage2 run `which compmake` $(out) -c "rmake"
	coverage html -d out_coverage --include '*src/mcdp*'

docoverage-parallel:
	# note you need "rmake" otherwise it will not be captured
	rm -rf ouf_coverage .coverage .coverage.*
	-DISABLE_CONTRACTS=1 comptests -o $(out) --nonose -c "exit" $(package)
	-DISABLE_CONTRACTS=1 coverage run --concurrency=multiprocessing  `which compmake` $(out) -c "rparmake"
	coverage combine
	coverage html -d out_coverage --include '*src/mcdp*'


clean:
	rm -rf $(out) _cached


stats-locs:
	wc -l `find . -type f -name '*.py' | grep -v test`

stats-locs-tests:
	wc -l `find . -type f -name '*.py' | grep test`



bump-upload:
	bumpversion patch
	git push --tags
	python setup.py sdist upload

readme-commands:
	mcdp-solve -d src/mcdp_data/libraries/examples/example-battery.mcdplib battery "<1 hour, 0.1 kg, 1 W>"
	mcdp-solve -d src/mcdp_data/libraries/examples/example-battery.mcdplib battery "<1 hour, 1.0 kg, 1 W>"

clean-branches:
	@echo First delete branches on Github.
	@echo Then run this command.
	@echo
	git fetch -p && git branch -vv | awk '/: gone]/{print $$1}' | xargs git branch -d


