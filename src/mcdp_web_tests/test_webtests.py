from comptests.registrar import run_module_tests
from mcdp import MCDPConstants
from mcdp.logs import logger
from mcdp_docs.preliminary_checks import assert_not_contains
from mcdp_library_tests.create_mockups import write_hierarchy
from mcdp_shelf.access import Privileges
from mcdp_utils_misc import dir_from_package_name, tmpdir
from mcdp_utils_misc.mis import repo_commit_all_changes
from mcdp_utils_xml.project_text import project_html
from mcdp_web.confi import parse_mcdpweb_params_from_dict
from mcdp_web.main import WebApp
from mcdp_web.resource_tree import MCDPResourceRoot
from mcdp_web_tests.spider import Spider
import os
import shutil
import unittest
import urlparse

from contracts.utils import raise_desc, indent
from git import Repo
from pyramid.security import Allow, Everyone


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
            authentication_ids: []
            groups: []
            subscriptions:
            - %s
            ''' % another_name_for_unittests_shelf,
        }
    }
    repo0 = create_empty_repo(where, bname)
    write_hierarchy(where, user_db_skeleton)
    repo_commit_all_changes(repo0)
    # checks that it use well formed
    #UserDB(where)
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
            unittests = os.path.join(mcdp_data, 'bundled.mcdp_repo','shelves', 'unittests.' + MCDPConstants.shelf_extension )
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
                'repos_yaml': """{
    'local': {
#         'user_db': '../mcdp-user-db/users',
#         'users': '../mcdp-user-db/users.mcdp_repo'
    },
    'remote': {}
    }"""
            }
            options = parse_mcdpweb_params_from_dict(settings)
            wa = WebApp(options, settings)
            app = wa.get_app()
            
            all_shelves = set()
            db_view = wa.hi.db_view
            for repo in db_view.repos.values():
                for shelf in repo.shelves:
                    all_shelves.add(shelf)
                    
            db_view.user_db['anonymous'].subscriptions = list(all_shelves)
            
            self.testapp = TestApp(app)

    def get_maybe_follow(self, url0):
        res = self.testapp.get(url0)
        if '302' in res.status:
            location = res.headers['location']
            url0 = urlparse.urljoin(res.request.url, location)
            res = res.follow()
        return url0, res
 
class FunctionalTestsSpider(FunctionalTests):
    def runTest(self):
        # turn off access control for user list
        MCDPResourceRoot.__acl__.append((Allow, Everyone, Privileges.ACCESS))
        MCDPResourceRoot.__acl__.append((Allow, Everyone, Privileges.VIEW_USER_LIST))
        MCDPResourceRoot.__acl__.append((Allow, Everyone, Privileges.VIEW_USER_PROFILE_PUBLIC))
        if MCDPConstants.test_spider_exclude_images:
            exclude = ['png','pdf','dot','svg','txt']
        else:
            exclude = []
                
        ushelf = '/repos/bundled/shelves/%s' % another_name_for_unittests_shelf
        bugs = [
            ushelf + '/libraries/basic/models/sum2f_rcomp/views/solver',
            ushelf + '/libraries/pop/models/pop_example_3_7_newsyntax/views/ndp_repr/',
            
            # this refers to a library that is not in this shelf
            ushelf + '/libraries/making/models/test1/views/syntax/',
            ushelf + '/libraries/documents/test_par.html',
            ushelf + '/libraries/documents/test_subfigures.html',
        ]
        for b in bugs:
            self.testapp.get(b)
            
        # this should not redirect
        url = '/repos/bundled/shelves/%s/libraries/documents/align.html'  % another_name_for_unittests_shelf
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
            if url == 'http://localhost/authomatic':
                return True 
            if 'confirm' in url:
                return True
            # > - http://localhost/confirm_creation_similar
            # > - http://localhost/confirm_bind
            # > - http://localhost/confirm_creation_create
            # > - http://localhost/confirm_bind_bind
            # > - http://localhost/confirm_creation
            if ':' in parsed.path:
                return True
            if 'exit' in parsed.path: # skip actions
                return True
            if parsed.netloc and parsed.netloc != u'localhost':
                return True
            
            if 'solver' in parsed.path:
                return True
            
            for x in exclude:
                if x in parsed.path: return True
            
            return False

        spider = Spider(self.get_maybe_follow, ignore=ignore)
         
        spider.visit(ushelf + '/libraries/making/models/test1/views/syntax/')
        spider.visit(ushelf + '/libraries/documents/test_subfigure.html')
        
        spider.visit('/tree')
        max_fails =  10
        max_pages = 100
        try:
            spider.go(max_fails=max_fails, max_pages=max_pages)
        except KeyboardInterrupt:
            pass
        spider.log_summary()
        if spider.skipped:
            for url in sorted(spider.skipped):
                logger.warn('Skipped %s' % url)
        if spider.failed or spider.not_found:
            msg = ''
            if spider.not_found:
                msg += 'These URLs not found:'
                for f, e in spider.not_found.items():
                    msg += '\n- %s' % f
                
            if spider.failed:
                msg += '\nErrors for these URLs:'
                for f, e in spider.failed.items():
                    msg += '\n- %s' % f
                    msg += '\n referrers: \n' + "\n  - ".join(spider.referrers[f])
                    
                if False:
                    for f, e in spider.failed.items():
                        msg += '\n URL: ' + f
                        msg += '\n referrers: \n' + "\n  - ".join(spider.referrers[f])
                        
                        body = e[e.index('<html'):]
                        s = project_html(body) 
                        msg += '\n' + indent(s, '  > ')
    #                 msg += '\n' + indent(str(e), '  > ')
#                 msg += '\n'.join('- %s' % _ for _ in sorted(spider.failed))
            raise_desc(Exception, msg)

#@comptest_fails
def check_tree():
    ft = FunctionalTestsSpider()
    ft.setUp()
    ft.runTest()



if __name__ == '__main__':
    run_module_tests()
#     check_tree()
    
    
    