# -*- coding: utf-8 -*-
import datetime
import urllib2
import urlparse

from authomatic import Authomatic
from authomatic.adapters import WebObAdapter
import git.cmd  # @UnusedImport
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import remember

from mcdp import logger
from mcdp_user_db import UserInfo
from mcdp_utils_misc import memoize_simple


@memoize_simple
def get_authomatic_config_(self):
    CONFIG = {}
    from authomatic.providers import oauth2
    if 'google.consumer_key' in self.settings:
        google_consumer_key = self.settings['google.consumer_key'] 
        google_consumer_secret = self.settings['google.consumer_secret']
        CONFIG['google'] = {                   
                'class_': oauth2.Google,
                'consumer_key':  google_consumer_key,
                'consumer_secret': google_consumer_secret,
                'scope': [
                    'https://www.googleapis.com/auth/plus.me',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile',
                ],
        }
        logger.info('Configured Google authentication.')
    else:
        logger.warn('No Google authentication configuration found.')
    
    if 'facebook.consumer_key' in self.settings:
        oauth2.Facebook.user_info_url = (
            'https://graph.facebook.com/v2.5/me?fields=id,first_name,last_name,picture,email,'
            'gender,timezone,location,middle_name,name_format,third_party_id,website,birthday,locale')
        facebook_consumer_key = self.settings['facebook.consumer_key'] 
        facebook_consumer_secret = self.settings['facebook.consumer_secret']
        CONFIG['facebook'] = {                   
                'class_': oauth2.Facebook,
                'consumer_key':  facebook_consumer_key,
                'consumer_secret': facebook_consumer_secret,
                'scope': ['public_profile', 'email'],
        }
        logger.info('Configured Facebook authentication.')
    else:
        logger.warn('No Facebook authentication configuration found.')
        
    if 'github.consumer_key' in self.settings:
        github_consumer_key = self.settings['github.consumer_key'] 
        github_consumer_secret = self.settings['github.consumer_secret']
        CONFIG['github'] =  {
            'class_': oauth2.GitHub,
            'consumer_key': github_consumer_key,
            'consumer_secret': github_consumer_secret,
            'access_headers': {'User-Agent': 'PyMCDP'},
        }
        logger.info('Configured Github authentication.')
    else:
        logger.warn('No Github authentication configuration found.')

    if 'linkedin.consumer_key' in self.settings:
        CONFIG['linkedin'] =  {
            'class_': oauth2.LinkedIn,
            'consumer_key': self.settings['linkedin.consumer_key'],
            'consumer_secret': self.settings['linkedin.consumer_secret'],
            'scope': ['r_emailaddress', 'r_basicprofile'],
        }
        logger.info('Configured Linkedin authentication.')
    else:
        logger.warn('No Linkedin authentication configuration found.')
#     
#     if 'amazon.consumer_key' in self.settings:
#         CONFIG['linkedin'] =  {
#             'class_': oauth2.Amazon,
#             'consumer_key': self.settings['amazon.consumer_key'],
#             'consumer_secret': self.settings['amazon.consumer_secret'],
# #             'scope': ['r_emailaddress', 'r_basicprofile'],
#         }
#         logger.info('Configured Amazon authentication.')
#     else:
#         logger.warn('No Amazon authentication configuration found.')
    
    return CONFIG


def view_authomatic_(self, config, e):
    response = Response()
    p = urlparse.urlparse(e.request.url)
    logger.info(p)
    if '127.0.0.1' in p.netloc:
        msg = 'The address 127.0.0.1 cannot be used with authentication.'
        raise ValueError(msg)
    provider_name = e.context.name
    logger.info('using provider %r' % provider_name)
    
    
    authomatic = Authomatic(config=config, secret='some random secret string')
    result = authomatic.login(WebObAdapter(e.request, response), provider_name)
    
    if not result:
        return response
    
    # If there is result, the login procedure is over and we can write to response.
    response.write('<a href="..">Home</a>')
    
    if result.error:
        # Login procedure finished with an error.
        response.status = 500
        response.write(u'<h2>Damn that error: {0}</h2>'.format(result.error.message))
        return response
    elif result.user:
        # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
        # We need to update the user to get more info.
        #if not (result.user.name and result.user.id):
        result.user.update()
        
        
        s = "user info: \n"
        for k, v in result.user.__dict__.items():
            s += '\n %s  : %s' % (k,v)
        print(s)
        
        next_location = e.root
        handle_auth_success(self, e, provider_name, result, next_location)

        response.write('<pre>'+s+'</pre>')
        # Welcome the user.
        response.write(u'<h1>Hi {0}</h1>'.format(result.user.name))
        response.write(u'<h2>Your id is: {0}</h2>'.format(result.user.id))
        response.write(u'<h2>Your email is: {0}</h2>'.format(result.user.email))
    
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
    #    a) if we can match the Openid with an existing account, because:
    #         i. same email  or
    #        ii. same name (ignore conflict for now)
    #       then we log in
    #    b) if not, we ask the user if they want to create an account.
    
    # get the data
    name = result.user.name
    email = result.user.email
    picture = result.user.picture
    if result.user.id is None:
        msg = 'Cannot obtain ID for authentication.'
        raise Exception(msg)
    
    if provider_name == 'github':
        candidate_username = result.user.username 
        website = result.user.data['blog']
        affiliation = result.user.data['company']
        unique_id = result.user.id
    elif provider_name == 'facebook':
        if name is None:
            msg = 'Could not get name from Facebook so cannot create username.'
            raise Exception(msg)

        candidate_username = name.replace(' ','_').lower() 
        website = None
        affiliation = None
        unique_id = result.user.id
    elif provider_name == 'google':
        if name is None:
            msg = 'Could not get name from Google so cannot create username.'
            raise Exception(msg)
        candidate_username = name.replace(' ','_').lower()
        website = result.user.link
        affiliation = None
        unique_id = result.user.id
#             * first_name
#             * gender
#             * id
#             * last_name
#             
    elif provider_name == 'linkedin':
        candidate_username = name.replace(' ', '_').lower()
        website = result.user.link
        affiliation = None
        unique_id = result.user.id
    else:
        assert False, provider_name
    best = self.user_db.match_by_id(provider_name, unique_id)
    #best = self.user_db.best_match(username, name, email)
    res = {}
    currently_logged_in = e.username is not None
    if currently_logged_in:
        if best is not None:
            if best.username ==  e.username:
                # do nothing
                res['message'] = 'Already authenticated'
                raise HTTPFound(location=next_location)
            else:
                logger.info('Switching user to %r.' % best.username)
                success_auth(self, e.request, best.username, next_location)
        else:
            # no match
            res['message'] = 'Do you want to bind account to this one?'
            confirm_bind = e.root + '/confirm_bind?user=xxx'
            raise HTTPFound(location=confirm_bind)
    else:
        # not logged in
        if best is not None:
            # user already exists: login 
            success_auth(self, e.request, best.username, next_location)
        else:
            # not logged in, and the user does not exist already
            # we create an accounts
            
            candidate_usernames = [candidate_username]
            
            
            username = self.user_db.find_available_user_name(candidate_usernames)
            res = {}
            res['username']= username
            res['name'] = name
            res['email'] = email
            res['website'] = website
            res['affiliation'] = affiliation
            res['account_last_active'] = datetime.datetime.now()
            res['account_created'] = datetime.datetime.now()
            res['authentication_ids'] = [ {'provider': provider_name,
                                           'id': unique_id}]
            logger.info('Reading picture %s' % picture)
            try:
                h = urllib2.urlopen(picture)
                logger.info('url opened  %s' % h)
                jpg = h.read()
                logger.info('read %s bytes' % len(jpg)) 
                res['picture'] = jpg
            except BaseException as e:
                logger.error(e)
                res['picture'] = None
            for k in res:
                if isinstance(res[k], unicode):
                    res[k] = res[k].encode('utf8')
            res['subscriptions'] = []
            res['groups'] = ['account_created_automatically',
                             'account_created_using_%s' % provider_name]
            u = UserInfo(**res) 
            self.user_db.create_new_user(u)
            
            success_auth(self, e.request, username, next_location)

def success_auth(self, request, username, next_location):
    if not username in self.user_db:
        msg = 'Could not find user %r' % username
        raise Exception(msg)
    logger.info('successfully authenticated user %s' % username)
    headers = remember(request, username)
    raise HTTPFound(location=next_location, headers=headers)
