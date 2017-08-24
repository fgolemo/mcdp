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
from mcdp_utils_misc.memoize_simple_imp import memoize_simple
from git.exc import GitCommandError


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

@memoize_simple
def get_all_files(dirname):
    all_files = locate_files(dirname, '*', include_directories=True)
    res = []
    for x in all_files:
        res.append(x)
        if os.path.isdir(x):
            res.append(x + '/')
        
    return sorted(res)

def resolve_reference(ref, defaults):
    
    for k, v in defaults.items():
        if getattr(ref, k, None) == None:
            ref = ref._replace(**{k:v})
    
    if ref.branch is None:
        ref = ref._replace(branch='master')
        
    tmpdir = '/tmp/git_repos'
    dirname = checkout_repository(tmpdir, ref.org, ref.repo, ref.branch)
    
    # now look for the file
    all_files = get_all_files(dirname)
    matches = []
    def does_match(a, short):
        return a.endswith('/' + short)
    
    for f in all_files:
        if does_match(f, ref.path):
            matches.append(f)
    if not matches:
        # print "\n".join(all_files)
        msg = 'Could not find reference to file %r.' % ref.path
        msg += '\n checkout in %s' % dirname
        msg += '\n' + str(ref)
        raise DPSemanticError(msg)
    if len(matches) > 1:
        msg = 'Multiple matches for %r.' % ref.path
        msg += '\n' +"\n".join(matches)
        raise DPSemanticError(msg)
    
    filename = os.path.realpath(matches[0])
    base= os.path.realpath(dirname)
    assert filename.startswith(base)
    rel_filename = filename.replace(base+'/', '')
    github_url = ('https://github.com/%s/%s/blob/%s/%s' % 
                  (ref.org, ref.repo, ref.branch, rel_filename))
    
    if os.path.isdir(filename):
        contents = None
    else:
        contents = open(filename).read()
        
        # now we can resolve from_text and to_text
        if ref.from_text is not None:
            ref = ref._replace(from_line = which_line(contents, ref.from_text, 0))
        if ref.to_text is not None:
            assert ref.from_line is not None
            tl = which_line(contents, ref.to_text, after_line=ref.from_line)
            ref = ref._replace(to_line = tl)
            
    if ref.from_line is not None:
        github_url += '#L%d' % (ref.from_line+1) # github is 1-based
    if ref.to_line is not None:
        github_url += '-L%d' % (ref.to_line+1)
            
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
    line = len(after[:i].split('\n')) -1 
    return line + after_line
    
def checkout_repository(tmpdir, org, repo, branch):
    
    if branch is None:
        branch = 'master'
    path = os.path.join(tmpdir, org, repo, branch)
    url = 'git@github.com:%s/%s.git' % (org, repo)        
    
    try:
        if not os.path.exists(path):
            
            checkout(path, url, branch)
        else:
            repo = Repo(path)
            try:
                # race condition
                repo.remotes.origin.pull()
            except:
                pass  
        return path
    except GitCommandError as e:
        msg = 'Could not checkout repository %s' % path
        raise_wrapped(DPSemanticError, e, msg)

def checkout(path, url, branch):
    logger.info('Cloning %s to %s' % (url, path))
    
    try:
        # ignore LFS files
        env = {'GIT_LFS_SKIP_SMUDGE': '1'}
        repo = Repo.clone_from(url, path, branch=branch, depth=1, env=env)
        logger.info('Clone done.') 
    
        head = repo.create_head(branch)
        head.checkout()
#         if branch != 'master':
#             repo.delete_head('master')
        return repo
    except:
        shutil.rmtree(path)
        raise 

    

if __name__ == '__main__':
    run_module_tests()
    
    