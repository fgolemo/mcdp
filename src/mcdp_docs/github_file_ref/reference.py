from collections import namedtuple
from contracts import contract
from contracts.utils import raise_wrapped
from comptests.registrar import run_module_tests, comptest


# Consider an URL of the type
# github:org=duckietown,repo=Software,path=![path],branch=branch,frag=frag
# 
# The keys:
# 
#     org
#     repo
#     path
#     branch
#     frag
#     line

GithubFileRef = namedtuple('GithubFileRef', 
                           ['org', 'repo', 'path', 'branch', 'frag', 'line'])

class InvalidGithubRef(ValueError):
    pass

@contract(s=str)
def parse_github_file_ref(s):
    """ 
        Parses a line of the type
    
        github:k=v,k=v
        
    """
    prefix = 'github:'
    try:
        if not s.startswith(prefix):
            msg = 'URL does not start with prefix %r.' % prefix
            raise InvalidGithubRef(msg)
        
        values = {}
        then = s[len(prefix):]
        pairs = then.split(',')
        #print 'pairs', pairs
        if not pairs:
            msg = 'Empty url'
            raise InvalidGithubRef(msg)
        for p in pairs:
            if not '=' in p:
                msg = 'Invalid pair %r'% p
                raise InvalidGithubRef(msg)
            i = p.index('=')
            k = p[:i]
            v = p[i+1:]
            if not v or not k:
                msg = 'Invalid pair %r.' % p
                raise InvalidGithubRef(msg)
            values[k] = v
        
        org = values.pop('org', None)
        repo = values.pop('repo', None)
        branch = values.pop('branch', None)
        frag = values.pop('frag', None)
        line = values.pop('line', None)
        if line is not None:
            line = int(line)
        path = values.pop('path', None)
        
        if values:
            msg = 'Additional keys %s' % sorted(values)
            raise InvalidGithubRef(msg)
        
        return GithubFileRef(org=org, repo=repo, branch=branch,
                             frag=frag, line=line, path=path)
    except InvalidGithubRef as e:
        msg = 'Cannot parse "%s":' % s
        raise_wrapped(InvalidGithubRef, e, msg, compact=True)
    

def expect_failure(s):
    try:
        parse_github_file_ref(s)
    except InvalidGithubRef:
        pass
    else:
        raise Exception('expected failure for %r' % s)
    
@comptest
def parse1():
    expect_failure('github')
    expect_failure('github:')
    expect_failure('github:path=')
    expect_failure('github:path=,')
    expect_failure('github:,')
    expect_failure('github:notexist=one')
        
@comptest
def parse2():
    s = 'github:path=name'
    r = parse_github_file_ref(s)
    assert r.path == 'name'
    s = 'github:org=name'
    r = parse_github_file_ref(s)
    assert r.org == 'name'        
    s = 'github:branch=name'
    r = parse_github_file_ref(s)
    assert r.branch == 'name'        
    s = 'github:line=3'
    r = parse_github_file_ref(s)
    assert r.line == 3        
    
        
if __name__ == '__main__':
    run_module_tests()
    
    