from copy import deepcopy
import os

from contracts import contract
from contracts.utils import indent
from git import Repo
from git.objects.blob import Blob
from git.objects.tree import Tree

from mcdp.logs import logger
from mcdp_hdb.disk_events import disk_event_file_create, disk_event_file_delete,\
    disk_event_file_modify, disk_event_file_rename, disk_event_dir_rename,\
    disk_event_interpret, disk_event_dir_create, disk_event_dir_delete
from mcdp_hdb.disk_struct import ProxyDirectory, assert_equal_disk_rep
from mcdp_utils_misc.my_yaml import yaml_dump
import shutil


@contract(repo=Repo)
def check_translation_gitrep_to_diskrep(repo, branch_name, out):
    wd = repo.working_tree_dir
    
    
    commits = list(reversed(list(repo.iter_commits(branch_name))))
    
    # make sure that commits[0] is the first
    for i in range(1, len(commits)):
        assert commits[i].parents[0] == commits[i-1]
    repo.head.reference = commits[0]
    repo.head.reset(index=True, working_tree=True)
    
    disk_rep0 = ProxyDirectory.from_disk(wd)
    disk_rep = deepcopy(disk_rep0)
    
    
    if os.path.exists(out):
        shutil.rmtree(out)
    if not os.path.exists(out):
        os.makedirs(out) 
        
    def write_file_(name, what):
        name = os.path.join(out, name)
        with open(name, 'w') as f:
            f.write(what)
        logger.info('wrote on %s' % name)
        
    def write_file(i, n, what):
        name = '%d-%s.txt' % (i, n)
        write_file_(name, what)
    
    logger.debug('Initial files: %s' % list(_.path for _ in commits[1].tree.traverse()))
    
    msg = ""
    for i, commit in enumerate(commits):
        d = disk_rep_from_git_tree(commit.tree)
        msg += '\n\n' + indent(d.tree(), ' tree at commit #%d | '%i)
    write_file_('00-commits.txt', msg)
    
    all_disk_events = []
    for i in range(1, len(commits)):
        write_file(i, 'a-disk_rep', disk_rep.tree())
        
        msg = ""
        for d in commits[i-1].diff(commits[i]):
            msg += '\n' + str(d)
        write_file(i, 'c-diffs', msg)    
        
        events = diskevents_from_diff(commits[i-1], commits[i])
        write_file(i, 'd-diskevents_from_diff', yaml_dump(events))
        
        for disk_event in events:
            disk_event_interpret(disk_rep, disk_event)
        all_disk_events.extend(events)
        
        write_file(i, 'e-disk_rep-after-diskevents', disk_rep.tree())
        
        repo.head.reference = commits[i]
        repo.head.reset(index=True, working_tree=True)
        supposedly = ProxyDirectory.from_disk(wd)
        write_file(i, 'f-supposedly', supposedly.tree())
        
        assert_equal_disk_rep(disk_rep, supposedly)

    logger.debug('wd: %s' % wd)
    return dict(disk_rep0=disk_rep0, disk_events=all_disk_events, disk_rep=disk_rep)

    
def disk_rep_from_git_tree(tree):
    filenames2contents = {} 
    d = ProxyDirectory()
    for x in tree.traverse():
        if isinstance(x, Blob):
            filename = x.path
            contents = x.data_stream.read()  
            filenames2contents[filename] = contents
    
    for path, contents in filenames2contents.items():
        d.create_file_path(path, contents)
        
    return d
    
    
def diskevents_from_diff(commit_a, commit_b):
    diff = commit_a.diff(commit_b)
    
    def dirname_name_from_path(path):
        path = path.encode('utf8')
        dirname = os.path.dirname(path)
        
        if dirname == '':
            dirname = ()
        else:
            dirname = tuple(dirname.split('/'))
        basename = os.path.basename(path)
        return dirname, basename
    _id= 'ID'
    who = {}
    events = []
    
    existing = set([_.path.encode('utf8') for _ in commit_a.tree.traverse()])
    # create hash directory -> everything contained
    dir2contents = {}
    for tree in commit_a.tree.traverse():
        if isinstance(tree, Tree):
            dir2contents[tree.path.encode('utf8')] = set()
        
    for blob in commit_a.tree.traverse():
        if isinstance(blob, Blob):
            path = blob.path
            for d in dir2contents:
                if path.startswith(d):
                    dir2contents[d].add(path)
    
    removed_files = set()
    
    for d in diff.iter_change_type('D'):
        removed_files.add(d.b_path)
        
    deleted_completely = set()
    
    deleted_by_deleting_dir = set()
    for di, di_contents in dir2contents.items():
        if all(x in removed_files for x in di_contents):
            print('detected that %s was removed completely' % di)
            deleted_completely.add(di)
    
    
    for di in deleted_completely:
        # do not do this if the parent was already deleted
        if os.path.dirname(di) in deleted_completely:
            continue
        else:
            dirname, name = dirname_name_from_path(di)
            print('%s -> %s, %s' % (di, dirname, name))
            deleted_by_deleting_dir.update(dir2contents[di])
            e = disk_event_dir_delete(_id, who, dirname=dirname, name=name)
            events.append(e)

    for d in diff.iter_change_type('D'):
        if d.b_path in deleted_by_deleting_dir:
            continue
        dirname, name = dirname_name_from_path(d.b_path)
        e = disk_event_file_delete(_id, who, dirname=dirname, name=name)
        events.append(e)

    logger.debug('trees: %s' % list(commit_a.tree.traverse()))
    logger.debug('existing: %s' % "\n- ".join(existing))
    
    for d in diff.iter_change_type('A'):
        dirname, name = dirname_name_from_path(d.b_path)
        # create all partial directories
        for i in range(1, len(dirname)+1):
            partial = dirname[:i]
            partial_path = "/".join(partial)
            if not partial_path in existing:
                logger.debug('I need to create directory %r' % partial_path)
                d2 = partial[:-1]
                n2 = partial[-1]
                e = disk_event_dir_create(_id, who, dirname=d2,name=n2)
                events.append(e)
                existing.add("/".join(partial))
                
        contents = d.b_blob.data_stream.read()  
        e = disk_event_file_create(_id, who, dirname=dirname, name=name, contents=contents)
        events.append(e)
    for d in diff.iter_change_type('M'):
        dirname, name = dirname_name_from_path(d.b_path)
        contents = d.b_blob.data_stream.read()  
        e = disk_event_file_modify(_id, who, dirname=dirname, name=name, contents=contents)
        events.append(e)
        
    dir_renames = set()
    for d in diff.iter_change_type('R'): # rename
        a_dirname, a_name = dirname_name_from_path(d.a_path)
        b_dirname, b_name = dirname_name_from_path(d.b_path)
        if a_dirname != b_dirname:
            dirname, name1, name2 = get_first_diff(d.a_path, d.b_path)
            dir_renames.add((tuple(dirname), name1, name2))
            
        else:
            e = disk_event_file_rename(_id, who, dirname=a_dirname, name=a_name, name2=b_name)
            events.append(e)
    
    for dirname,name1,name2 in dir_renames:     
        e = disk_event_dir_rename(_id, who, dirname=dirname, name=name1, name2=name2)
        events.append(e)
            
    return events

def get_first_diff(a,b ):
    
    a = a.encode('utf8')
    b = b.encode('utf8')
    a = a.split('/')
    b = b.split('/')
    n = 0
    while a[n] == b[n]:
        n += 1

    assert a[:n] == b[:n], (a,b,n)
    dirname = a[:n]
    name1 = a[n]
    name2 = b[n]
    sol = dirname, name1, name2
    print('a = %s   b = %s  n = %s sol = %s' % (a,b,n,sol))
    return sol
    


