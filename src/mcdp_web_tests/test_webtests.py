import os
import unittest
import urlparse

from contracts.utils import raise_desc
from git import Repo

from comptests.registrar import run_module_tests, comptest
from mcdp.constants import MCDPConstants
from mcdp_library_tests.create_mockups import write_hierarchy
from mcdp_repo.repo_interface import repo_commit_all_changes
from mcdp_user_db import UserDB
from mcdp_utils_misc import tmpdir
from mcdp_web.confi import parse_mcdpweb_params_from_dict
from mcdp_web.main import WebApp
from mcdp_web_tests.spider import Spider
from mcdp_utils_misc.dir_from_package_nam import dir_from_package_name
import shutil


def create_empty_repo(d, bname):
    repo0 = Repo.init(d)
    filename = os.path.join(d, 'readme.txt')
    
    open(filename, 'wb').close()
    repo0.index.add([filename])
    repo0.index.commit("Adding "+filename+ "to repo")

    new_branch = repo0.create_head(bname)
    new_branch.checkout()
    fn = os.path.join(d, 'readme')
    with open(fn, 'w') as f:
        f.write('ciao')
    repo0.index.add([fn])
    repo0.index.commit('msg')
    return repo0

def create_user_db_repo(where, bname):
    user_db_skeleton = {
        'anonymous.%s' % MCDPConstants.user_extension: {
            MCDPConstants.user_desc_file: '''
            name: Anonymous user
            subscriptions:
            - unittests2
            ''',
        }
    }
    repo0 = create_empty_repo(where, bname)
    write_hierarchy(where, user_db_skeleton)
    repo_commit_all_changes(repo0)
    # checks that it use well formed
    UserDB(where)
    return repo0

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from webtest import TestApp
        
        with tmpdir(erase=False) as d:
            # create a db
            bname = 'master'
            userdb_remote = os.path.join(d, 'userdb_remote')
            repo0 = create_user_db_repo(userdb_remote, bname)
           
            mcdp_data = dir_from_package_name('mcdp_data')
            unittests = os.path.join(mcdp_data, 'libraries', 'unittests.' + MCDPConstants.shelf_extension )
            assert os.path.exists(unittests), unittests
            dest = os.path.join(userdb_remote, 'unittests2.' + MCDPConstants.shelf_extension )
            shutil.copytree(unittests, dest)
            repo_commit_all_changes(repo0)
            
            
            userdb = os.path.join(d, 'userdb')
            repo = Repo.init(userdb)
            origin = repo.create_remote('origin', url=userdb_remote)
            origin.fetch()

            head = repo.create_head(bname, origin.refs[bname])
            head.set_tracking_branch(origin.refs[bname])  # set local "master" to track remote "master
            head.checkout()
            settings = {
                'users': userdb,
                'load_mcdp_data': '0',
            }
            options = parse_mcdpweb_params_from_dict(settings)
            wa = WebApp(options)
            app = wa.get_app()
            self.testapp = TestApp(app)

    def get_maybe_follow(self, url0):
        res = self.testapp.get(url0)
        if '302' in res.status:
            location = res.headers['location']
            url0 = urlparse.urljoin(res.request.url, location)
            res = res.follow()
        return url0, res
 
    def runTest(self):
        spider = Spider(self.get_maybe_follow)
        spider.visit('/tree')
        spider.go()
        spider.log_summary()
        if spider.failed:
            msg = 'Could not get some URLs'
            raise_desc(Exception, msg, failed=list(spider.failed))

@comptest
def check_tree():
    ft = FunctionalTests()
    ft.setUp()
    ft.runTest()


if __name__ == '__main__':
    run_module_tests()
    
    
    
    