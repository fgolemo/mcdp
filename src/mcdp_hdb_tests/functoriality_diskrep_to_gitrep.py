from contracts.utils import indent
from git.util import Actor

from mcdp.logs import logger
from mcdp_hdb.disk_events import apply_disk_event_to_filesystem
from mcdp_hdb.diskrep_utils import assert_diskreps_same
from mcdp_hdb.gitrepo_map import gitrep_from_diskrep, diskrep_from_gitrep
from mcdp_utils_misc.my_yaml import yaml_dump


def check_translation_diskrep_to_gitrep(disk_rep0, disk_events, disk_rep1, out):
    if not disk_events:
        raise ValueError('no disk events')
    repo = gitrep_from_diskrep(disk_rep0)
    wd = repo.working_tree_dir
    readback = diskrep_from_gitrep(repo)
    assert_diskreps_same(disk_rep0, readback, 'original', 'written back')
    logger.debug(wd)
    logger.debug('\n'+indent(readback.tree(), 'read back |'))
    logger.debug('\n'+indent(yaml_dump(disk_events), 'disk_events|'))
    commits = []
    for disk_event in disk_events:
        logger.debug(indent(yaml_dump(disk_event), 'disk_event | '))
        apply_disk_event_to_filesystem(wd, disk_event)
        
        if repo.untracked_files:
            logger.debug('adding untracked file %r' % repo.untracked_files) 
            repo.index.add(repo.untracked_files)
        
        diff_index = repo.index.diff(None) 
        for d in diff_index.iter_change_type('A'):
            repo.index.add([d.b_path])
        for d in diff_index.iter_change_type('M'):
            repo.index.add([d.b_path])
        for d in diff_index.iter_change_type('D'):
            repo.index.remove([d.b_path])
        for d in diff_index.iter_change_type('R'): # rename
            repo.index.rename(d.a_path, d.b_path)
            
        message = yaml_dump(disk_event)
        actor = disk_event['who']['actor']
        system = disk_event['who']['host']['hostname']
        author = Actor(actor, None)
        committer = Actor(system, None)
#         logger.debug('2) all added')
#         system_cmd_show(wd, ['git', 'status'])
        commit = repo.index.commit(message, author=author, committer=committer)
        commits.append(commit)
#         logger.debug('3) after commit')
#         system_cmd_show(wd, ['git', 'status'])
    
    res = {}
    res['repo'] = repo
    return res
    logger.info('done for wd %s' % wd)

