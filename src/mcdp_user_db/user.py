from contracts import contract
from git.util import Actor



class UserInfo():
    
    def __init__(self, username, name, password, email, website, affiliation, groups, subscriptions):
        self.username = username
        self.name = name
        self.password = password
        self.email = email
        self.website = website
        self.affiliation = affiliation
        self.groups = groups
        self.subscriptions = subscriptions
        
    def get_gravatar(self, size):
        if self.email is not None:
            return gravatar(self.email, size)
        else:
            return gravatar('invalid@invalid.com', size)
    
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
        if self.email is None:
            res['gravatar64'] = self.get_gravatar(64)
            res['gravatar32'] = self.get_gravatar(32)
        else:
            res['gravatar64'] = self.get_gravatar(64)
            res['gravatar32'] = self.get_gravatar(32)
            
        return res
    
    def as_git_actor(self):
        hostname = 'hostname' # XXX
        email = '%s@%s' % (self.username, hostname)
        author = Actor(self.username, email)
        return author
    
# name: Andrea Censi
# email: acensi@ethz.ch
# website: https://censi.science/
# password: editor
# affiliation: ETH Zurich
# groups: [admin]
# 
# subscriptions:
# - u_andrea_private
# - u_andrea_public
# - u_andrea_subscription
# - u_maxxon_motors

@contract(s=dict)    
def userinfo_from_yaml(s,username):
    res = {}
    res['username']=username
    res['name'] = s.pop('name', None)
    res['password'] = s.pop('password', None)
    res['email'] = s.pop('email', None)
    res['website'] = s.pop('website', None)
    res['affiliation'] = s.pop('affiliation', None)
    res['subscriptions'] = s.pop('subscriptions', [])
    res['groups'] = s.pop('groups', [])
    return UserInfo(**res) 

def yaml_from_userinfo(user):
    res = {}
    res['name'] = user.name
    res['password'] = user.password
    res['email'] = user.email
    res['website'] = user.website
    res['affiliation'] = user.affiliation
    res['subscriptions'] = user.subscriptions
    res['groups'] = user.groups
    return res

def gravatar(email, size, default=None):
    import urllib, hashlib
    digest = hashlib.md5(email.lower()).hexdigest()
    gravatar_url = "https://www.gravatar.com/avatar/" + digest + "?"
    p = {}
    p['s'] = str(size)
    if default:
        p['d'] = default
    gravatar_url += urllib.urlencode(p)
    
    return gravatar_url
