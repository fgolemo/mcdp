import os
import shutil
import unittest
import urlparse

from contracts.utils import raise_desc, indent
from git import Repo

from comptests.registrar import run_module_tests, comptest
from mcdp import MCDPConstants
from mcdp_docs.preliminary_checks import assert_not_contains
from mcdp_library_tests.create_mockups import write_hierarchy
from mcdp_repo.repo_interface import repo_commit_all_changes
from mcdp_user_db import UserDB
from mcdp_utils_misc import dir_from_package_name, tmpdir
from mcdp_web.confi import parse_mcdpweb_params_from_dict
from mcdp_web.main import WebApp
from mcdp_web_tests.spider import Spider


# do not make relative to start using python
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

another_name_for_unittests_shelf = 'unittests'

def create_user_db_repo(where, bname):
    user_db_skeleton = {
        'anonymous.%s' % MCDPConstants.user_extension: {
            MCDPConstants.user_desc_file: '''
            name: Anonymous user
            subscriptions:
            - %s
            ''' % another_name_for_unittests_shelf,
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
            dest = os.path.join(userdb_remote, another_name_for_unittests_shelf + '.' + MCDPConstants.shelf_extension )
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
        ushelf = '/repos/global/shelves/%s' % another_name_for_unittests_shelf
        bugs = [
            ushelf + '/libraries/basic/models/sum2f_rcomp/views/solver',
            ushelf + '/libraries/pop/models/pop_example_3_7_newsyntax/views/ndp_repr/',
            
            # this refers to a library that is not in this shelf
            ushelf + '/libraries/making/models/test1/views/syntax/',
            ushelf + '/libraries/documents/test_par.html',
        ]
        for b in bugs:
            self.testapp.get(b)
            
        # this should not redirect
        url = '/repos/global/shelves/%s/libraries/documents/align.html'  % another_name_for_unittests_shelf
        res = self.testapp.get(url)
        if '302' in res.status:
            msg = 'Document redirect: %s -> %s' % (url, res.headers['location'])
            msg += '\n' + indent(res.body, '> ')
            raise Exception(msg)
        
        # another test
        _, res = self.get_maybe_follow('/tree/')
        assert_not_contains(res.body, 'None')
        
        # another test
        _, res = self.get_maybe_follow('/repos/')
        assert_not_contains(res.body, 'None')

        _, res = self.get_maybe_follow('/')
        assert_not_contains(res.body, 'function shelf')
         

        def ignore(url, parsed):  # @UnusedVariable
            if ':' in parsed.path:
                return True
            if 'exit' in parsed.path: # skip actions
                return True
            if parsed.netloc and parsed.netloc != u'localhost':
                return True
            
            if 'solver' in parsed.path:
                return True
            
            exclude = ['png','pdf','dot','svg','txt']
            for x in exclude:
                if x in parsed.path: return True
            
            return False

        spider = Spider(self.get_maybe_follow, ignore=ignore)
         
        spider.visit(ushelf + '/libraries/making/models/test1/views/syntax/')
        
        spider.visit('/tree')
        try:
            spider.go(max_fails=10)
        except KeyboardInterrupt:
            pass
        spider.log_summary()
        if spider.failed:
            msg = 'Could not get some URLs:\n'
            for f, e in spider.failed.items():
                msg += '\n URL: ' + f
                msg += '\n referrers: \n' + "\n  - ".join(spider.referrers[f]) 
                msg += '\n' + indent(str(e), '  > ')
#                 msg += '\n'.join('- %s' % _ for _ in sorted(spider.failed))
            raise_desc(Exception, msg)

@comptest
def check_tree():
    ft = FunctionalTests()
    ft.setUp()
    ft.runTest()


if __name__ == '__main__':
    run_module_tests()
    
    
    
    