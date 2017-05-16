# -*- coding: utf-8 -*-
from comptests.registrar import run_module_tests, comptest
from mcdp_docs.github_edit_links import org_repo_from_url


@comptest
def test_parsing():
    url = 'git@github.com:duckietown/duckuments.git'
    org, repo = org_repo_from_url(url)
    assert org == 'duckietown'
    assert repo == 'duckuments'
    
if __name__ == '__main__':
    run_module_tests()