from git.util import Actor


class User(object):
    def get_picture_jpg(self):
        ''' Returns the picture in JPG or None '''
        if 'user' in self.images:
            return self.images['user'].jpg
        else:
            return None
        
def as_utf8(s):
    if s is None:
        return s.decode('utf8')
    else:
        return None
    
class UserInfo(object):
    
#     def __init__(self, username, name, authentication_ids, email, website, affiliation, groups,
#                   subscriptions, picture,
#                   account_created,
#                   account_last_active,
#                   ):
#         self.username = username
#         self.name = name
#         self.authentication_ids = authentication_ids
#         self.email = email
#         self.website = website
#         self.affiliation = affiliation
#         self.groups = groups
#         self.subscriptions = subscriptions
#         self.picture = picture
#         self.account_created = account_created
#         self.account_last_active = account_last_active 
        
#     def get_gravatar(self, size):
#         if self.get_email() is not None:
#             return gravatar(self.email, size)
#         else:
#             return gravatar('invalid@invalid.com', size)
    
    def get_name(self):
        return as_utf8(self.name)
    
    def get_email(self):
        return self.email
    
    def get_affiliation_u(self):
        ''' Returns affiliation as unicode string '''    
        return as_utf8(self.affiliation)
        
    def get_groups(self):
        return self.groups
    
    def get_subscriptions(self):
        return self.subscriptions
    
    def __repr__(self):
        return 'UserInfo(%s)' % self.dict_for_page()
    
    def dict_for_page(self):
        res = {
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'website': self.website,
            'affiliation': self.affiliation,
            'groups': self.groups,
            'subscriptions': self.subscriptions,
        }
#         if self.email is None:
#             res['gravatar64'] = self.get_gravatar(64)
#             res['gravatar32'] = self.get_gravatar(32)
#         else:
#             res['gravatar64'] = self.get_gravatar(64)
#             res['gravatar32'] = self.get_gravatar(32)
#             
        return res
    
    def get_external_providers(self):
        """ Returns str -> id """
        res = {}
        for x in self.authentication_ids:
            provider = x.provider
            if x.id is not None:
                _id = x.id
            else: 
                _id = None
            res[provider] = _id
        return res
        
    def as_git_actor(self):
        hostname = 'hostname' # XXX
        email = '%s@%s' % (self.username, hostname)
        author = Actor(self.username, email)
        return author
    
# name: Andrea Censi
# email: acensi@ethz.ch
# website: https://censi.science/
# authentication_ids:
#    password: editor
# affiliation: ETH Zurich
# groups: [admin]
# 
# subscriptions:
# - u_andrea_private
# - u_andrea_public
# - u_andrea_subscription
# - u_maxxon_motors
# 
# @contract(s=dict)    
# def userinfo_from_yaml(s, username):
#     res = {}
#     s0 = dict(**s)
#     res['username']=username
#     res['name'] = s.pop('name', None)
#     res['authentication_ids'] = s.pop('authentication_ids', [])
#     res['email'] = s.pop('email', None)
#     res['website'] = s.pop('website', None)
#     res['affiliation'] = s.pop('affiliation', None)
#     res['subscriptions'] = s.pop('subscriptions', [])
#     res['groups'] = s.pop('groups', [])
#     res['account_last_active'] = s.pop('account_last_active', None)
#     res['account_created'] = s.pop('account_created', None)
#     res['picture'] = None
#     if s:
#         msg = 'Unknown fields: %s.' % format_list(s)
#         msg += '\nOriginal: \n'
#         msg += indent(yaml_dump(s0), '> ')
#         raise ValueError(msg)
#     return UserInfo(**res) 
# 
# def yaml_from_userinfo(user):
#     res = {}
#     res['name'] = user.name
#     res['authentication_ids'] = user.authentication_ids
#     res['email'] = user.email
#     res['website'] = user.website
#     res['affiliation'] = user.affiliation
#     res['subscriptions'] = user.subscriptions
#     res['account_created'] = user.account_created
#     res['account_last_active'] = user.account_last_active
#     res['groups'] = user.groups
#     return res
# 
# def gravatar(email, size, default=None):
#     import urllib, hashlib
#     digest = hashlib.md5(email.lower()).hexdigest()
#     gravatar_url = "https://www.gravatar.com/avatar/" + digest + "?"
#     p = {}
#     p['s'] = str(size)
#     if default:
#         p['d'] = default
#     gravatar_url += urllib.urlencode(p)
#     
#     return gravatar_url
