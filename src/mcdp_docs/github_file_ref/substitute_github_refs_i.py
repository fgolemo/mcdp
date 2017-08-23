import os
import shutil

from bs4.element import Tag
from contracts.utils import raise_wrapped, raise_desc, indent
from git.repo.base import Repo

from comptests.registrar import comptest, run_module_tests
from mcdp.exceptions import DPSyntaxError, DPSemanticError
from mcdp.logs import logger
from mcdp_docs.github_file_ref.reference import parse_github_file_ref,\
    InvalidGithubRef
from mcdp_utils_misc.locate_files_imp import locate_files
from mcdp_utils_xml.add_class_and_style import add_class
from mcdp_utils_xml.parsing import bs


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
    

    ref = resolve_reference(ref, defaults)
    logger.debug(ref.url)
    a.attrs['href'] = ref.url
    
    if not list(a.children):
        c = Tag(name='code')
        add_class(c, 'github-resource-link')
        c.append(os.path.basename(ref.path))
        a.append(c)

def resolve_reference(ref, defaults):
    
    for k, v in defaults.items():
        if getattr(ref, k, None) == None:
            ref = ref._replace(**{k:v})
    
    if ref.branch is None:
        ref = ref._replace(branch='master')
        
    tmpdir = '/tmp/git_repos'
    dirname = checkout_repository(tmpdir, ref.org, ref.repo, ref.branch)
    
    # now look for the file
    all_files = locate_files(dirname, '*')
    matches = []
    for f in all_files:
        if f.endswith(ref.path):
            matches.append(f)
    if not matches:
        print "\n".join(all_files)
        msg = 'Could not find reference to file %r.' % ref.path
        msg += '\n checkout in %s' % dirname
        raise DPSemanticError(msg)
    if len(matches) > 1:
        msg = 'Multiple matches for %r.' % ref.path
        raise DPSemanticError(msg)
    
    filename = os.path.realpath(matches[0])
    base= os.path.realpath(dirname)
    assert filename.startswith(base)
    rel_filename = filename.replace(base+'/', '')
    github_url = ('https://github.com/%s/%s/blob/%s/%s' % 
                  (ref.org, ref.repo, ref.branch, rel_filename))
    contents = open(filename).read()
    
    # now we can resolve from_text and to_text
    if ref.from_text is not None:
        ref = ref._replace(from_line = which_line(contents, ref.from_text, 0))
    if ref.to_text is not None:
        assert ref.from_line is not None
        tl = which_line(contents, ref.to_text, after_line=ref.from_line)
        ref = ref._replace(to_line = tl)
        
    if ref.from_line is not None:
        github_url += '#L%d' % ref.from_line
    if ref.to_line is not None:
        github_url += '-L%d' % ref.to_line
            
    ref = ref._replace(contents=contents) 
    ref = ref._replace(url=github_url)
    ref = ref._replace(path=filename)
    return ref
    
def which_line(contents, fragment, after_line):
    lines = contents.split('\n')
    after = "\n".join(lines[after_line:])
    if not fragment in contents:
        msg = 'Cannot find fragment %r in file after line %d' % (fragment, after_line)
        msg += '\n' + indent(after, '| ')
        raise DPSemanticError(msg)
    i = after.index(fragment)
    line = len(after[:i].split('\n'))
    return line + after_line
    
def checkout_repository(tmpdir, org, repo, branch):
    if branch is None:
        branch = 'master'
    path = os.path.join(tmpdir, org, repo, branch)
    
    if not os.path.exists(path):
        url = 'git@github.com:%s/%s.git' % (org, repo)        
        checkout(path, url, branch)
    else:
        repo = Repo(path)
        repo.remotes.origin.pull()  
    return path

def checkout(path, url, branch):
    logger.info('Cloning %s to %s' % (url, path))
    
    try:
        # ignore LFS files
        env = {'GIT_LFS_SKIP_SMUDGE': '1'}
        repo = Repo.clone_from(url, path, depth=1, env=env)
        logger.info('Clone done.') 
    
        head = repo.create_head(branch)
        head.checkout()
        if branch != 'master':
            repo.delete_head('master')
        return repo
    except:
        shutil.rmtree(path)
        raise 

@comptest
def sub1():
    defaults = {'org': 'AndreaCensi', 
                'repo': 'mcdp',
                'branch': 'duckuments'}
     
    s = """
<a href="github:path=context_eval_as_constant.py"></a> 
"""
    soup = bs(s)
    n = substitute_github_refs(soup, defaults)
    assert n == 1
    
    s2 = str(soup)
    logger.debug(indent(s2, '  '))
    
    expect = '<code class="github-resource-link">context_eval_as_constant.py</code>'
    if not expect in s2:
        raise Exception(s2)
    

@comptest
def sub2():
    defaults = {'org': 'AndreaCensi', 
                'repo': 'mcdp',
                'branch': 'duckuments'}
     
    s = """
<a href="github:path=context_eval_as_constant.py,from_text=get_connections_for,to_text=return"></a> 
"""
    soup = bs(s)
    n = substitute_github_refs(soup, defaults)
    assert n == 1
    
    s2 = str(soup)
    logger.debug('\n'+indent(s2, '  '))
    
    expect=  'context_eval_as_constant.py#L7-L12'
    
    if not expect in s2:
        raise Exception('No %s in %s' % (expect, s2))
    
    
    
    
    
        
if __name__ == '__main__':
    run_module_tests()