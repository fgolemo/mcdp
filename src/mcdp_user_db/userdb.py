import os
import yaml
from mcdp_user_db.user import userinfo_from_yaml, yaml_from_userinfo
from mcdp.logs import logger

class UserDB():

    def __init__(self, userdir):
        self.users = {}
        us = load_users(userdir)
        self.userdir = userdir
        self.users.update(us)
        
    def __contains__(self, key):
        return key in self.users
    
    def __getitem__(self, key):
        if key is None:
            key = 'anonymous'
        return self.users[key]
    
    def exists(self, login):
        return login in self
    
    def authenticate(self, login, password):
        user = self.users[login]
        return password == user.password
    
    def save_user(self, username):
        filename = os.path.join(self.userdir, username, USER_FILE)
        user = self.users[username]
        y = yaml_from_userinfo(user)
        s = yaml.dump(y)
        logger.info('Saving %r:\n%s' % (username, s))
        with open(filename, 'w') as f:
            f.write(s)
            
        
USER_FILE = 'user.yaml'

def load_users(userdir):
    ''' Returns a dictionary of username -> User profile '''
    users = {}
    
    if not os.path.exists(userdir):
        msg = 'Directory %s does not exist' % userdir
        Exception(msg)
        
    for user in os.listdir(userdir):
        if user.startswith('.'):
            continue
        info = os.path.join(userdir, user, 'user.yaml')
        if not os.path.exists(info):
            msg = 'Info file %s does not exist.'  % info
            raise Exception(msg)
        data = open(info).read()
        s = yaml.load(data)
        
        users[user] = userinfo_from_yaml(s, user)
    return users
        