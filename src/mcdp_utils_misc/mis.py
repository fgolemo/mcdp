from git.util import Actor

def repo_commit_all_changes(repo, message=None, author=None):
    if author is None:
        author = Actor("system","system")
    if message is None:
        message = ""
    if repo.untracked_files: 
        repo.index.add(repo.untracked_files)
      
    modified_files = repo.index.diff(None)
    for m in modified_files:
        repo.index.add([m.b_path])
          
    commit = repo.index.commit(message, author=author)
    return commit