from comptests.registrar import comptest, run_module_tests
from mcdp_utils_misc.my_yaml import yaml_load
from mcdp_hdb_mcdp.main_db_schema import DB

@comptest
def test_create_user():
    candidate = """
    info:
      username: andrea_censi
      website: https://www.linkedin.com/in/censi
      name: Andrea Censi
      subscriptions: []
      account_last_active: 2017-04-15 09:19:17.981656
      affiliation:
      authentication_ids:
      - id: ldmBacWwYm
        provider: linkedin
        password: 
      groups:
      - account_created_automatically
      - account_created_using_linkedin
      email: linkedin@censi.org
      account_created: 2017-04-15 09:19:17.981751
    images:
      user:
        jpg: 'binary'
        pdf: 
        png:
        svg:
    """
    user_data = yaml_load(candidate)
    # create empty DB
    user_db_data = {'users': {}}
    user_db_view = DB.view_manager.create_view_instance(DB.user_db, user_db_data)
    user_db_view.set_root()
    user = DB.view_manager.create_view_instance(DB.user, user_data)
    user.set_root()
    print user.info.get_email()
    print user.info.get_name()
    user_db_view.create_new_user('andrea_censi', user)
    
if __name__ == '__main__':
    run_module_tests()