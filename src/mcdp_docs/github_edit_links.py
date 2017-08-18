# -*- coding: utf-8 -*-

import os, re

from git.repo.base import Repo


def get_repo_root(d):
    ''' Returns the root of the repo root, or raise ValueError. '''
    if os.path.exists(os.path.join(d, '.git')):
        return d
    else:
        parent = os.path.dirname(d)
        if not parent:
            msg = 'Could not find repo root'
            raise ValueError(msg)
        return get_repo_root(parent)
    
def add_edit_links(soup, filename):
    # is this is in a repo?
    try: 
        repo_root = get_repo_root(filename)
    except ValueError:
        return
    
    repo_info = get_repo_information(repo_root)
    branch = repo_info['branch']
    # commit = repo_info['commit']
    org = repo_info['org']
    repo = repo_info['repo']
    relpath = os.path.relpath(filename, repo_root)
    
    repo_base = 'https://github.com/%s/%s' % (org, repo)
    blob_base = repo_base + '/blob/%s' % (branch)
    edit_base = repo_base + '/edit/%s' % (branch)
    
    blob_url = blob_base + "/" + relpath
    edit_url = edit_base + "/" + relpath
    
    for h in soup.findAll(['h1','h2','h3','h4']):
        h.attrs['github-edit-url'] = edit_url
        h.attrs['github-blob-url'] = blob_url


def get_repo_information(repo_root):
    gitrepo = Repo(repo_root)
    branch = gitrepo.active_branch
    commit = gitrepo.head.commit.hexsha
    url = gitrepo.remotes.origin.url
   
    # now github can use urls that do not end in '.git'
    if 'github' in url and not url.endswith('.git'):
        url = url + '.git'
    org, repo = org_repo_from_url(url)
    return dict(branch=branch, commit=commit, org=org, repo=repo)


def org_repo_from_url(url):
    # 'git@host:<org>/<repo>.git'
    pattern = r':(.*)/(.*)\.git'
    # search() = only part of the string
    match = re.search(pattern=pattern, string=url)
    if not match:
        msg = 'Cannot match this url string: %r' % url
        msg += ' with this regexp: %s' % pattern
        raise NotImplementedError(msg)
    org = match.group(1)
    repo = match.group(2)
    return org, repo
