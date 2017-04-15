import os

from contracts import contract
import yaml

from mcdp import MCDPConstants
from mcdp.logs import logger
from .user import UserInfo
from mcdp_utils_misc import format_list, locate_files
from datetime import datetime


__all__ = ['UserDB']

class UserDB(object):

#     def __init__(self, userdir):
#         self.users = {}
#         us = load_users(userdir)
#         self.userdir = userdir
#         self.users.update(us)
#         
#         if not MCDPConstants.USER_ANONYMOUS in self.users:
#             msg = 'Need account for the anonymous user "%s".' % MCDPConstants.USER_ANONYMOUS
#             raise_desc(ValueError, msg, found=self.users)
#             
        
    def __contains__(self, key):
        return key in self.users
    
    def match_by_id(self, provider, provider_id):
        for u in self.users.values():
            for w in u.info.authentication_ids:
                if w.provider == provider and w.id == provider_id:
                    return u
        return None
        
    def best_match(self, username, name, email):
        if username is not None:
            if username in self.users:
                return self.users[username]

        for u in self.users.values():
            user_info = u.info
            if name is not None and user_info.get_name() == name:
                return u
            if email is not None and user_info.get_email() == email:
                return u
            
        return None
     
    @contract(returns=UserInfo)
    def __getitem__(self, key):
        if key is None:
            key = 'anonymous'
        u = self.users[key].info
        return u
    
    def exists(self, login):
        return login in self
    
    @contract(returns=bool)
    def authenticate(self, login, password):
        user_info = self.users[login].info
        for p in user_info.authentication_ids:
            if p.provider == 'password':
                pwd = p.password
                match = password == pwd
                if not match:
                    msg = 'Password %s does not match with stored %s.' % (password, pwd)
                    logger.warn(msg)
                    
                    user_info.account_last_active = datetime.now()
                return match
        
        return False
    
    @contract(returns=str)
    def find_available_user_name(self, candidate_usernames):
        for x in candidate_usernames:
            if x not in self.users:
                return x
        for i in range(2,10):
            for x in candidate_usernames:
                y = '%s%d' % (x, i)
                if y not in self.users:
                    return y
        raise ValueError(candidate_usernames)
    
    def create_new_user(self, username, u):
        if username in self.users:
            msg = 'User "%s" already present.'
            raise ValueError(msg)
        self.users[username] = u
#         self.save_user(username, new_user=True)
#     
#     def save_user(self, username, new_user=False):
#         userdir = os.path.join(self.userdir, username + '.' + MCDPConstants.user_extension)
#         if not os.path.exists(userdir):
#             if new_user:
#                 os.makedirs(userdir)
#             else:
#                 msg = 'Could not find user dir %r.' % userdir
#                 raise ValueError(msg)
# 
#         filename = os.path.join(userdir,  MCDPConstants.user_desc_file)
#         if not os.path.exists(filename) and not new_user:
#             msg = 'Could not find user filename %r.' % filename
#             raise ValueError(msg)
#         user = self.users[username]
#         y = yaml_from_userinfo(user)
#         s = yaml.dump(y)
#         logger.info('Saving %r:\n%s' % (username, s))
#         with open(filename, 'w') as f:
#             f.write(s)
#             
# #         if user.picture is not None:            
# #             fn = os.path.join(userdir, MCDPConstants.user_image_file)
# #             with open(fn, 'wb') as f:
# #                 f.write(user.picture)
#         logger.debug('Saved user information here: %s' % userdir)
        
    def get_unknown_user_struct(self, username):
        s = {}
        return userinfo_from_yaml(s, username)

def load_users(userdir):
    ''' Returns a dictionary of username -> User profile '''
    users = {}
    
    exists = os.path.exists(userdir) 
    if not exists:
        msg = 'Directory %s does not exist' % userdir
        raise Exception(msg)
        
    assert exists
        
    l = locate_files(userdir, 
                     pattern='*.%s' % MCDPConstants.user_extension, 
                     followlinks=True,
                     include_directories=True,
                     include_files=False)
    
    for userd in l:
        username = os.path.splitext(os.path.basename(userd))[0]
        info = os.path.join(userd, MCDPConstants.user_desc_file)
        if not os.path.exists(info):
            msg = 'Info file %s does not exist.'  % info
            raise Exception(msg)
        data = open(info).read()
        s = yaml.load(data)
        
        users[username] = userinfo_from_yaml(s, username)
        
        f = os.path.join(userd, MCDPConstants.user_image_file)
        if os.path.exists(f):
            users[username].picture = open(f, 'rb').read()
        
    if not users:
        msg = 'Could not load any user from %r' % userdir
        raise Exception(msg)
    else:
        logger.info('loaded users: %s.' % format_list(sorted(users)))
        
    return users
        