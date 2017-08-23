from comptests.registrar import comptest, run_module_tests
from mcdp_utils_xml.parsing import bs
from mcdp_docs.github_file_ref.reference import parse_github_file_ref,\
    InvalidGithubRef
from mcdp.exceptions import DPSyntaxError, DPSemanticError
from contracts.utils import raise_wrapped, raise_desc
import os
from git.repo.base import Repo

from git import RemoteProgress
from mcdp.logs import logger
from mcdp_utils_misc.locate_files_imp import locate_files
import shutil

class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        p = cur_count / (max_count or 100.0)
#         print(p)
        #op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")
# end
def substitute_github_refs(soup, defaults):
    n = 0 
    
    for a in soup.find_all('a'):
        href = a.attrs.get('href', '')
        if href.startswith('github:'):
            substitute_github_ref(a, defaults)
            n += 1
        
    return n
    
def substitute_github_ref(a, defaults):
    href = a.attrs['href']
    try:
        ref = parse_github_file_ref(href)
    except InvalidGithubRef as e:
        msg = 'Could not parse a reference in %s.'  % str(a)
        raise_wrapped(DPSyntaxError, e, msg, compact=True)
        
    if ref.path is None:
        msg = 'There is no path specified.'
        raise_desc(DPSyntaxError, e, msg, ref=ref)
        
    
    for k, v in defaults.items():
        if getattr(ref, k, None) == None:
            ref = ref._replace(**{k:v})
            
    tmpdir = '/tmp/git_repos'
    dirname = checkout_repository(tmpdir, ref.org, ref.repo, ref.branch)
    
    # now look for the file
    all_files = locate_files(dirname, '*')
    matches = []
    for f in all_files:
        if f.endswith(ref.path):
            matches.append(f)
    if not matches:
        msg = 'Could not find reference to file %r.' % ref.path
        msg += '\n checkout in %s' % dirname
        raise DPSemanticError(msg)
    
    
    
def checkout_repository(tmpdir, org, repo, branch):
    path = os.path.join(tmpdir, org, repo, branch)
    
    if not os.path.exists(path):
        url = 'git@github.com:%s/%s.git' % (org, repo)        
        checkout(path, url, branch)
          
    return path

def checkout(path, url, branch):
    logger.info('Cloning %s to %s' % (url, path))
    # ignore LFS files
    try:
        env = {'GIT_LFS_SKIP_SMUDGE': '1'}
        repo = Repo.clone_from(url, path, depth=1, env=env, progress=MyProgressPrinter())
        logger.info('Clone done.')
    # 
    #     from git import Repo
    #     repo = Repo.init(path)
    #     #author = Actor("system", "system@%s" % host_name())
    #     #repo.index.commit('initial commit', author=author, committer=author)
    # 
    #     origin = repo.create_remote('origin', url=url)
    #     assert origin.exists()
    #     origin.fetch()
    
        head = repo.create_head(branch)
        head.checkout()
        if branch != 'master':
            repo.delete_head('master')
    except:
        shutil.rmtree(path)
        raise

    # create a local branch at the latest fetched master. We specify the name statically, but you have all
    # information to do it programatically as well.
#     bare_master = bare_repo.create_head('master', origin.refs.master)
#     bare_repo.head.set_reference(bare_master)

@comptest
def sub1():
    defaults = {'org': 'AndreaCensi', 
                'repo': 'mcdp',
                'branch': 'duckuments'}
     
    s = """

<a href="github:path=substitute_github_refs.py">path</a> 
"""
    soup = bs(s)
    n = substitute_github_refs(soup, defaults)
    assert n == 1
    
    
        
if __name__ == '__main__':
    run_module_tests()