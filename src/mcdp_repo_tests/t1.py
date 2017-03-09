from nose.tools import assert_raises

from comptests.registrar import comptest, run_module_tests
from mcdp_repo.repo_interface import repo_from_url,\
    RepoInvalidURL
from mcdp_utils_misc.fileutils import tmpdir
from git.repo.base import Repo
import os


@comptest
def test_invalid_urls():
    # must start with mcdp
    assert_raises(RepoInvalidURL, repo_from_url, 'mcdp:git:/filename')
    
@comptest
def test_repo_urls():
    with tmpdir('test_repo_urls', erase=False) as d:
            
        urls = [
            'mcdpr:git:%s' % (d + '/' + 'local_repo'),
            'mcdpr:git:git://github.com',
            'mcdpr:git:https://github.com/',
            'mcdpr:git:ssh://git@github.com/<user>/<repo>',
            'mcdpr:gh:<user>/<module>',
            'mcdpr:python:<module>',
            'mcdpr:pip:<egg>/<module>',
        ]
    
        for i, url in enumerate(urls):
            id_repo = 'r%02d' % i
        
            repo = repo_from_url(url)

@comptest
def test_invalid_repo_name():
    repo = repo_from_url('mcdpr:python:package_not_existing')
    assert repo.available() == False
    s = repo.get_availability_error()
    assert 'Cannot find' in s, s

@comptest
def test_valid_repo_python():
    repo = repo_from_url('mcdpr:python:mcdp_data')
    assert repo.available() == True
    shelves = repo.get_shelves()
    assert len(shelves) > 2
    print('shelves: %s' % list(shelves))

@comptest
def test_valid_repo_git():
    with tmpdir() as d:
        r0 = os.path.join(d, 'repo0')
        repo0 = Repo.init(r0)
        
        r1 = os.path.join(d, 'repo1')
#         repo1 = Repo.init(r1)
        repo1 = repo0.clone(r1)

    
if __name__ == '__main__':
    run_module_tests()