from contracts import contract
from decent_params import DecentParams


def describe_mcdpweb_params(dp):
    dp.add_int('load_mcdp_data', default=1)
    dp.add_int('allow_anonymous', default=1, help='Allow anonymous access')
    dp.add_int('allow_anonymous_write', default=1, help='Allow anonymous write')
    
    dp.add_bool('allow_user_login', default=True)
    dp.add_bool('allow_user_signups', default=False)
    
    dp.add_string('config', short='-c', default=None, 
                  help='Reads .ini file configuration.') 
    dp.add_string('libraries', short='-d',default=None, 
                  help='Library directories containing models.') 
                  
    dp.add_string('instance', default='local')
    default = """
{}
    """
    dp.add_string('repos_yaml', default=default, help='Repository configuration file')
    
    dp.add_bool('libraries_writable', default=True)
    dp.add_string('users', help='Directories for user data.', default=None)
    
    dp.add_int('port', default=8080, help='Port to listen to.')
    
    dp.add_string('url_base_internal', default=None)
    dp.add_string('url_base_public', default=None)
    for p in ['facebook', 'google', 'linkedin', 'github', 'amazon']:
        dp.add_string('%s_consumer_key' % p, default=None)
        dp.add_string('%s_consumer_secret' % p, default=None)
    
    # deprecated
    dp.add_bool('delete_cache', default=True, help='(deprecated)')
    return dp

@contract(x=dict)
def parse_mcdpweb_params_from_dict(x):
    dp = DecentParams()
    describe_mcdpweb_params(dp)
    return dp.get_dpr_from_dict(x)
