 
out=out/comptests

package=mcdp_tests


prepare_tests:
	mkdir -p $(out)

	$(MAKE) -C libraries/unittests/basic.mcdplib/generated_dps/ clean all

comptests: prepare_tests
	comptests -o $(out) --contracts --nonose --console $(package)

comptests-nocontracts: prepare_tests
	comptests -o $(out) --nonose --console $(package)

comptests-run: prepare_tests
	comptests -o $(out) --contracts --nonose $(package) 

comptests-run-nocontracts: prepare_tests
	comptests -o $(out) --nonose $(package) 
	compmake $(out) -c "ls failed"

comptests-run-nocontracts-console: prepare_tests
	comptests -o $(out) --nonose $(package) --console

comptests-run-parallel: prepare_tests
	comptests -o $(out) --contracts --nonose -c "rparmake" $(package)  

comptests-run-parallel-nocontracts: prepare_tests
	DISABLE_CONTRACTS=1 comptests -o $(out) --nonose -c "rparmake" $(package)  

comptests-run-parallel-nocontracts-onlysetup: prepare_tests
	DISABLE_CONTRACTS=1 comptests -o $(out) --nonose -c "parmake dynamic and ready; parmake dynamic and ready; parmake dynamic and ready" $(package)  

comptests-run-parallel-nocontracts-cov: prepare_tests
	DISABLE_CONTRACTS=1 comptests -o $(out) --coverage --nonose -c "rparmake" $(package)  

comptests-run-parallel-nocontracts-prof: prepare_tests
	DISABLE_CONTRACTS=1 comptests -o $(out) --profile --nonose -c "make; rparmake" $(package)  


docoverage-single: prepare_tests
	# note you need "rmake" otherwise it will not be captured
	rm -rf ouf_coverage .coverage
	-DISABLE_CONTRACTS=1 comptests -o $(out) --nonose -c "exit" $(package)
	-DISABLE_CONTRACTS=1 coverage2 run `which compmake` $(out) -c "rmake"
	coverage html -d out_coverage --include '*src/mcdp*'

docoverage-parallel: prepare_tests
	# note you need "rmake" otherwise it will not be captured
	rm -rf ouf_coverage .coverage .coverage.*
	-DISABLE_CONTRACTS=1 comptests -o $(out) --nonose -c "exit" $(package)
	-DISABLE_CONTRACTS=1 coverage run --concurrency=multiprocessing  `which compmake` $(out) -c "rparmake"
	coverage combine
	$(MAKE) coverage-report
	#coverage html -d out_coverage --include '*src/mcdp*'

coverage-report:
	coverage html -d out_coverage --include '*src/mcdp*'


clean:
	rm -rf $(out) out/opt_basic_*
	#_cached


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

check-unicode-encoding-line:
	grep 'coding: utf-8' -r --include '*.py' -L  src/

clean-branches:
	@echo First delete branches on Github.
	@echo Then run this command.
	@echo
	git fetch -p && git branch -vv | awk '/: gone]/{print $$1}' | xargs git branch -d


naked-prints:
	zsh -c "grep '^[[:space:]]*print ' src/**/*py 2>/dev/null  | grep -v gvgen | grep -v pyparsing_bundled | grep -v /libraries | grep -v XCP | grep -v node_modules | grep -v tests"
