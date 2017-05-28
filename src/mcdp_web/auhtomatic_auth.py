# -*- coding: utf-8 -*-
import datetime

from authomatic import Authomatic
from authomatic.adapters import WebObAdapter
from authomatic.providers import oauth2
from contracts.utils import check_isinstance
import git.cmd  # @UnusedImport
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import remember
from system_cmd import system_cmd_result

from mcdp import logger
from mcdp_hdb_mcdp.main_db_schema import DB
from mcdp_user_db.user import User
from mcdp_utils_misc import memoize_simple


@memoize_simple
def get_authomatic_config_(self):
    CONFIG = {}    
    if self.options.google_consumer_key is not None:
        CONFIG['google'] = {                   
                'class_': oauth2.Google,
                'consumer_key':  self.options.google_consumer_key,
                'consumer_secret': self.options.google_consumer_secret,
                'scope': [
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile',
                ],
        }
        logger.info('Configured Google authentication.')
    else:
        logger.warn('No Google authentication configuration found.')
    
    if self.options.facebook_consumer_key is not None:
        oauth2.Facebook.user_info_url = (
            'https://graph.facebook.com/v2.5/me?fields=id,first_name,last_name,picture,email,'
            'gender,timezone,location,middle_name,name_format,third_party_id,website,birthday,locale')
        CONFIG['facebook'] = {                   
                'class_': oauth2.Facebook,
                'consumer_key':  self.options.facebook_consumer_key,
                'consumer_secret': self.options.facebook_consumer_secret,
                'scope': ['public_profile', 'email'],
        }
        logger.info('Configured Facebook authentication.')
    else:
        logger.warn('No Facebook authentication configuration found.')
        
    if self.options.github_consumer_key is not None:
        CONFIG['github'] =  {
            'class_': oauth2.GitHub,
            'consumer_key':  self.options.github_consumer_key,
            'consumer_secret':  self.options.github_consumer_secret,
            # todo: implement
            'scope': [#'user', 
                      'user:email'],
            'access_headers': {'User-Agent': 'PyMCDP'},
        }
        logger.info('Configured Github authentication.')
    else:
        logger.warn('No Github authentication configuration found.')
        
    if self.options.amazon_consumer_key is not None:
        CONFIG['amazon'] =  {
            'class_': oauth2.Amazon,
            'consumer_key': self.options.amazon_consumer_key,
            'consumer_secret': self.options.amazon_consumer_secret,
            'scope': ['profile'],
            
        }
        logger.info('Configured Amazon authentication.')
    else:
        logger.warn('No Amazon authentication configuration found.')

    if self.options.linkedin_consumer_key is not None:
        CONFIG['linkedin'] =  {
            'class_': oauth2.LinkedIn,
            'consumer_key': self.options.linkedin_consumer_key,
            'consumer_secret': self.options.linkedin_consumer_secret,
            'scope': ['r_emailaddress', 'r_basicprofile'],
        }
        logger.info('Configured Linkedin authentication.')
    else:
        logger.warn('No Linkedin authentication configuration found.') 
    
    return CONFIG


def view_authomatic_(self, config, e):
    response = Response()
    provider_name = e.context.name
    logger.info('using provider %r' % provider_name)
    if not provider_name in config:
        msg = 'I got to the URL for provider %r even though it is not in the config.' % provider_name
        raise ValueError(msg)
    authomatic = Authomatic(config=config, secret='some random secret string')
    url_base_public = self.options.url_base_public
    url_base_internal = self.options.url_base_internal
    if not ((url_base_public is None)==(url_base_public is None)):
        msg = 'Only one of url_base_public and url_base_internal is specified.'
        raise Exception(msg)
    result = authomatic.login(MyWebObAdapter(e.request, response, url_base_internal, url_base_public), 
                              provider_name)
    if not result: 
        return response
    
    # If there is result, the login procedure is over and we can write to response.
    response.write('<a href="..">Home</a>')
    
    if result.error:
        # Login procedure finished with an error.
        msg = result.error.message
        return self.show_error(e, msg, status=500)
    elif result.user:
        # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
        # We need to update the user to get more info.
        #if not (result.user.name and result.user.id):
        result.user.update()
        
        s = "user info: \n"
        for k, v in result.user.__dict__.items():
            s += '\n %s  : %s' % (k,v)
        logger.debug(s)
        
        next_location = config.get('next_location', e.root)
        handle_auth_success(self, e, provider_name, result, next_location)
# 
#         response.write('<pre>'+s+'</pre>')
#         # Welcome the user.
#         response.write(u'<h1>Hi {0}</h1>'.format(result.user.name))
#         response.write(u'<h2>Your id is: {0}</h2>'.format(result.user.id))
#         response.write(u'<h2>Your email is: {0}</h2>'.format(result.user.email))
    
    # just regular login
    return response
    
def handle_auth_success(self, e, provider_name, result, next_location):
    assert result.user
    # 1) If we are currently logged in:
    #    a) if we match to current account, do nothing.
    #    b) if we match with another account, log with that account
    #    c) if we don't match, ask the user if they want to bound
    #        this account to the MCDP account
    # 2) If we are not currently logged in:
    #    a) if we can match the Openid with an existing account based on ID
    #       then we log in
    #    b) If not:
    #         - if there is a soft match (same email or same name) but not provider-id match
    #           We ask for confirmation: "We found this other account; are you sure? maybe
    #           you want to log in using the other provider"
    #         - else, we ask the user if they want to create an account.
    #           
    
    user_db = self.hi.db_view.user_db
    # Get the candidate user 
    u = get_candidate_user(user_db, result, provider_name)
    check_isinstance(u, User)
    # we should already have an id
    assert  u.info.authentication_ids[0].provider == provider_name
    unique_id = u.info.authentication_ids[0].id 
    
    best = user_db.match_by_id(provider_name, unique_id)
    
    currently_logged_in = e.username is not None
    if currently_logged_in:
    
        # if we match with 
        if best is not None:
            best_username = best.info.username

            # if we match to current account
            if best_username ==  e.username:
                # do nothing
                logger.info('We are already authenticated to same account.')
                raise HTTPFound(location=next_location)
            else:
                # W
                logger.info('Switching user to %r.' % best_username)
                success_auth(self, e.request, best_username, next_location)
        else:
            # no match
            e.session.candidate_user = u
            e.session.soft_match = None
            e.session.next_location = next_location
            self.redirect_to_page(e, '/confirm_bind/')
    
    if not currently_logged_in:
        # not logged in
        if best is not None:
            best_username = best.info.username

            # user already exists: login 
            success_auth(self, e.request, best_username, next_location)
        else:
            # not logged in, and the user does not exist already
            
            # check if there are other accounts with same email or same name
            soft_match = user_db.best_match(None, u.info.name, u.info.email)
            
            if soft_match is not None:
                # we should present a page in which we confirm whether this is correct
                # we save the user in the session
                e.session.candidate_user = u
                e.session.soft_match = soft_match
                e.session.next_location = next_location
                self.redirect_to_page(e, '/confirm_creation_similar/') 
            else:
                # we will create an accounts
                e.session.candidate_user = u
                e.session.soft_match = None
                e.session.next_location = next_location
                self.redirect_to_page(e, '/confirm_creation/') 
                 

    
                
def view_confirm_bind_(self, e):
    u = e.session.candidate_user
    if u is None:
        msg = "Page has expired."
        return self.show_error(e, msg) 
    res = {
        'candidate_user': u,
    } 
    return res

def view_confirm_bind_bind_(self, e):
    u = e.session.candidate_user
    if u is None:
        msg = "Page has expired."
        return self.show_error(e, msg)
    u0 = e.user
    # todo: also compy names
    u0.authentication_ids.extend(u.authentication_ids)
    for x in ['email','name','affiliation', 'picture', 'website']:
        if getattr(u0, x) is None:
            setattr(u0, x, getattr(u, x))
    
    user_db = self.hi.db_view.user_db
    user_db.users[u0.username] = u0
#     self.user_db.save_user(u0.username)
    
    res = {
        'next_location': e.session.next_location,
    } 
    return res

def view_confirm_creation_similar_(self, e):
    soft_match = e.session.soft_match
    candidate_user = e.session.candidate_user
    if soft_match is None:
        msg = "Page has expired."
        return self.show_error(e, msg)
    res = {
        'soft_match': soft_match,
        'candidate_user': candidate_user,
    } 
    return res

def view_confirm_creation_(self, e):
    u = e.session.candidate_user
    if u is None:
        msg = "Page has expired."
        return self.show_error(e, msg)
    res = {
        'candidate_user': u, 
    }
    return res;

def view_confirm_creation_create_(self, e):
    next_location = e.session.next_location
    u = e.session.candidate_user
    if u is None:
        msg = "Page has expired."
        return self.show_error(e, msg)
    e.session.candidate_user = u
    user_db = self.hi.db_view.user_db
    user_db.create_new_user(u.info.username, u)
    success_auth(self, e.request, u.info.username, next_location)
    return {}


def get_candidate_user(user_db, result, provider_name):
    ''' Returns a candidate UserInfo structure as observed from Oauth response '''
    # get the data
    name = result.user.name
    email = result.user.email
    
    if result.user.id is None:
        msg = 'Cannot obtain ID for authentication.'
        raise Exception(msg)
#     if email is None:
#         msg = 'Cannot obtain email address'
#         raise Exception(msg)
    
    if provider_name == 'github':
        candidate_username = result.user.username 
        website = result.user.data['blog']
        affiliation = result.user.data['company']
        unique_id = result.user.id
        picture = result.user.picture
    elif provider_name == 'facebook':
        if name is None:
            msg = 'Could not get name from Facebook so cannot create username.'
            raise Exception(msg)

        candidate_username = name.encode('utf8').replace(' ','_').lower() 
        website = None
        affiliation = None
        unique_id = result.user.id
        picture = result.user.picture
    elif provider_name == 'google':
        if name is None:
            msg = 'Could not get name from Google so cannot create username.'
            raise Exception(msg)
        candidate_username = name.encode('utf8').replace(' ','_').lower()
        website = result.user.link
        affiliation = None
        unique_id = result.user.id 
        picture = result.user.picture
    elif provider_name == 'linkedin':
        candidate_username = name.encode('utf8').replace(' ', '_').lower()
        website = result.user.link
        affiliation = None
        unique_id = result.user.id
        picture = result.user.picture
    elif provider_name == 'amazon':
        candidate_username = name.encode('utf8').replace(' ', '_').lower()
        website = result.user.link
        affiliation = None
        unique_id = result.user.id
        picture = None
    else:
        assert False, provider_name
    candidate_usernames = [candidate_username]
            
    username = user_db.find_available_user_name(candidate_usernames)
    res = {}
    res['username'] = username
    res['name'] = name
    res['email'] = email
    res['website'] = website
    res['affiliation'] = affiliation
    res['account_last_active'] = datetime.datetime.now()
    res['account_created'] = datetime.datetime.now()
    res['authentication_ids'] = [ {'provider': provider_name,
                                   'id': unique_id, 'password': None}]
    logger.info('Reading picture %s' % picture)
    if picture is None:
        jpg = None
    else:
        try:
            local_filename = 'pic.jpg'
            cwd = '.'
            cmd = ['wget', '-O', local_filename, picture]
            system_cmd_result(cwd, cmd,
              display_stdout=True,
              display_stderr=True,
              raise_on_error=True)
            # local_filename, headers = urlretrieve(picture)
            with open(local_filename, 'rb') as f:
                jpg = f.read()
            logger.info('read %s bytes' % len(jpg)) 
        except BaseException as exc:
            logger.error(exc)
            jpg = None
    for k in res:
        if isinstance(res[k], unicode):
            res[k] = res[k].encode('utf8')
    res['subscriptions'] = []
    res['groups'] = ['account_created_automatically',
                     'account_created_using_%s' % provider_name]
    data = {'info': res,
            'images':{'user':{'jpg':jpg, 'png':None, 'svg': None, 'pdf': None}}} 
    
#     logger.debug('new user:\n%s' % yaml_dump(data))
    
    user = DB.view_manager.create_view_instance(DB.user, data)
    user.set_root()
    return user

def success_auth(self, request, username, next_location):
    if not username in self.hi.db_view.user_db:
        msg = 'Could not find user %r' % username
        raise Exception(msg)
    logger.info('successfully authenticated user %s' % username)
    headers = remember(request, username)
    raise HTTPFound(location=next_location, headers=headers)


class MyWebObAdapter(WebObAdapter):
    """Adapter for the |webob|_ package."""
    
    def __init__(self, request, response, url_base_internal, url_base_public):
        self.request = request
        self.response = response
        self.url_base_internal = url_base_internal
        self.url_base_public = url_base_public

    @property
    def url(self):
        url =  self.request.path_url
        if self.url_base_internal is not None:
            url = url.replace(self.url_base_internal, self.url_base_public)
        return url
    
    
# 
# def transform_location(Location, url_base_internal, url_base_public):
#     Location_parsed = urlparse.urlparse(Location)    
# #     logger.info('redir url: %s' % str(Location_parsed))
#     qs = dict(urlparse.parse_qsl(Location_parsed.query, keep_blank_values=1, strict_parsing=1))
# #     logger.info('query: %s' % qs)
# #     logger.info('query: %s' % type(qs))
#     redirect_uri = qs.get('redirect_uri',None)
#     logger.info('redirect_uri: %s' % redirect_uri)
#     if redirect_uri is None:
#         msg = 'Expected to see redirect_uri in response.'
#         raise_desc(ValueError, msg, Location=Location, qs=qs)
# #     assert isinstance(redirect_uri, list)
# #     redirect_uri = redirect_uri[0]
#     if not redirect_uri.startswith(url_base_internal):
#         msg = 'Expected redirect_uri to start with url_base_internal.'
#         raise_desc(ValueError, msg, redirect_uri=redirect_uri, url_base_internal=url_base_internal)
#     redirect_uri2 = redirect_uri.replace(url_base_internal, url_base_public)
#     qs['redirect_uri'] = redirect_uri2
# #     print('redirect_uri2: %s' % redirect_uri2)
#     query2 = urllib.urlencode(qs)
# #     print('query2: %s' % query2)
#     
#     scheme, netloc, path, params, _, fragment = Location_parsed
#     Location2 = urlunparse((scheme, netloc, path, params, query2, fragment))
#     return Location2 
#     
# def fix_response(response, url_base_internal, url_base_public):
#     for i, (a, b) in list(enumerate(response.headerlist)):
# #         logger.warn('%r | %r' % (a,b))
#         if a == 'Location---':
#             Location = b
#             Location2 = transform_location(Location, url_base_internal, url_base_public)
#             logger.warn('rewritten reposnse:\na %s\nb %s' % (Location, Location2))
#             response.headerlist[i] = (a, Location2)
#     return response
