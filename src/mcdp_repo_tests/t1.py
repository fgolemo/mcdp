# import os
# 
# from git.repo.base import Repo
# from nose.tools import assert_raises
# 
# from comptests.registrar import comptest, run_module_tests
# from mcdp_library_tests.create_mockups import mockup_flatten
# from mcdp_repo.repo_interface import repo_from_url, RepoInvalidURL, MCDPGitRepo
# from mcdp_shelf_tests.shelves import setup_shelve_01
# from mcdp_utils_misc.fileutils import tmpdir
# 
# 
# @comptest
# def test_invalid_urls():
#     # must start with mcdp
#     assert_raises(RepoInvalidURL, repo_from_url, 'mcdp:git:/filename')
#     
# # @comptest
# def test_repo_urls():
#     with tmpdir('test_repo_urls', erase=False) as d:
#             
#         urls = [
#             'mcdpr:git:%s' % (d + '/' + 'local_repo'),
#             'mcdpr:git:git://github.com',
#             'mcdpr:git:https://github.com/',
#             'mcdpr:git:ssh://git@github.com/<user>/<repo>',
#             'mcdpr:gh:<user>/<module>',
#             'mcdpr:python:<module>',
#             'mcdpr:pip:<egg>/<module>',
#         ]
#     
#         for i, url in enumerate(urls):
#             id_repo = 'r%02d' % i
#         
#             repo = repo_from_url(url)
# 
# @comptest
# def test_invalid_repo_name():
#     repo = repo_from_url('mcdpr:python:package_not_existing')
#     assert repo.available() == False
#     s = repo.get_availability_error()
#     assert 'Cannot find' in s, s
# 
# @comptest
# def test_valid_repo_python():
#     repo = repo_from_url('mcdpr:python:mcdp_data')
#     assert repo.available() == True
#     shelves = repo.get_shelves()
#     assert len(shelves) > 2
#     print('shelves: %s' % list(shelves))
# 
# def create_file_and_yield(files0, d):
#     flattened = mockup_flatten(files0)
#     for filename, contents in flattened.items():
#         fn = os.path.join(d, filename)
#         dn = os.path.dirname(fn)
#         if not os.path.exists(dn):
#             os.makedirs(dn)
#             
#         with open(fn, 'w') as f:
#             f.write(contents)
#         yield fn
# 
# @comptest
# def test_valid_repo_git():
#     with tmpdir(erase=False) as d:
#         r0 = os.path.join(d, 'repo0')
#         repo0 = Repo.init(r0)
#         
#         from git import Actor
#         author = Actor("John", "john@mcdp")
#         
#         for filename in create_file_and_yield(setup_shelve_01, r0):
# #             print('written %r' % filename)
# #             print('untracked_files: %s' % repo0.untracked_files)
# #             print('Dirty: %s' % repo0.is_dirty(untracked_files=True))
#             repo0.index.add(repo0.untracked_files)
#             message = 'author: system'
#             repo0.index.commit(message, author=author)
#         
#         mcdpr = MCDPGitRepo(url=r0, where=os.path.join(d, 'repo_cloned'))
#         
#         r1 = os.path.join(d, 'repo1')
# #         repo1 = Repo.init(r1)
#         repo1 = repo0.clone(r1)
# 
#     
# if __name__ == '__main__':
#     run_module_tests()