from contracts import contract
from decent_params import DecentParams


def describe_mcdpweb_params(dp):
    dp.add_int('load_mcdp_data', default=1)
    dp.add_int('allow_anonymous', default=1)
    dp.add_bool('allow_user_login', default=True)
    dp.add_bool('allow_user_signups', default=False)
    dp.add_bool('delete_cache', default=True)
    dp.add_string('libraries', short='-d',default=None, 
                  help='Library directories containing models.') 
                  
    dp.add_bool('libraries_writable', default=True)
    dp.add_string('users', help='Directories for user data.', default=None)
    return dp

@contract(x=dict)
def parse_mcdpweb_params_from_dict(x):
    dp = DecentParams()
    describe_mcdpweb_params(dp)
    return dp.get_dpr_from_dict(x)
