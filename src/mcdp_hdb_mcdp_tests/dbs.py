from mcdp_utils_misc.my_yaml import yaml_load
from mcdp_hdb_mcdp.main_db_schema import DB

def testdb1():
    ''' returns a db '''
    
    user_info_andrea = yaml_load("""
    username: andrea
    website: https://censi.science/
    name: Andrea Censi
    subscriptions:
    - examples
    - HEPA
    - unittests
    - examples_devel
    - FDM
    - uav_energetics
    - mcdp_uncertainty
    account_last_active:
    affiliation: "ETH Zurich"
    authentication_ids:
    - password: mine
      id:
      provider: password
    groups:
    - FDM
    - admin
    email: censi@mit.edu
    account_created:
""")
    db0 = {
        'repos': {},
        'user_db' : {
            'users': {
                'andrea': { 'info': user_info_andrea, 'images': {} },
            }
        }
    }
    
    DB.db.validate(db0)
    return db0

    