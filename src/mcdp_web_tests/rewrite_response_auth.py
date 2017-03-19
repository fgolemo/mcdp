from comptests.registrar import comptest, run_module_tests
import urlparse
from mcdp.logs import logger
from mcdp_web.auhtomatic_auth import transform_location

@comptest
def rewrite():
    Location = ('https://github.com/login/oauth/authorize?'
        'scope=&state=3eb22eeb9e5c8966990638310f&'+
        'redirect_uri=http%3A%2F%2Flocalhost%2Fauthomatic%2Fgithub&'
        +'response_type=code&client_id=ea4bb597623a1f6f6c7')
    url_base_internal = 'http://localhost' 
    url_base_public = url_base_internal
    
    Location2 = transform_location(Location, url_base_internal, url_base_public)

    
    print('Location: %s' % Location)
    print('Location2: %s' % Location2)
    assert Location == Location2
                

if __name__ == '__main__':
    run_module_tests()