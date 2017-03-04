# -*- coding: utf-8 -*-
from collections import namedtuple

from contracts import contract
from mcdp.logs import logger
from contracts.utils import indent
from pyramid.security import Allow, Authenticated, Everyone, Deny

USER_ANONYMOUS = 'anonymous'
PRIVILEGE_DISCOVER = 'discover'
PRIVILEGE_SUBSCRIBE = 'subscribe'
PRIVILEGE_READ = 'read'
PRIVILEGE_WRITE = 'write'
PRIVILEGE_ADMIN = 'admin'
PRIVILEGE_ACCESS = 'access'
PRIVILEGE_ALL = 'all'
PRIVILEGES = [PRIVILEGE_DISCOVER, PRIVILEGE_SUBSCRIBE, PRIVILEGE_READ, PRIVILEGE_WRITE, PRIVILEGE_ADMIN, 
              PRIVILEGE_ACCESS, PRIVILEGE_ALL]

ACLRule = namedtuple('ACLRule', 'allow_or_deny to_whom privilege')

class ACL():
    def __init__(self, rules):
        self.rules = rules
        
        
    def as_pyramid_acl(self):
        res = []
        for r in self.rules:
            a = {'Allow': Allow, 'Deny': Deny}[r.allow_or_deny]
            b = {'Everyone': Everyone, 'Authenticated': Authenticated}.get(r.to_whom, r.to_whom)
            c = r.privilege    
            res.append((a,b,c))
        return res
        
        
    def allowed2(self, privilege, user):
        return self.allowed(privilege, user.username, user.groups)
    
    def allowed(self, privilege, username, groups):
        principals = []
        principals.append('Everyone')
        if username is not None and username != USER_ANONYMOUS:
            principals.append('Authenticated')
            principals.append(username)
        if groups:
            for g in groups:
                principals.append('groups:%s'%g)
        
        return self.allowed_(privilege, principals)
    
    def allowed_(self, privilege, principals):
        if not privilege in PRIVILEGES:
            msg = 'Unknown privilege %r' % privilege
            raise ValueError(msg)
        
        for r in self.rules:
            if r.privilege == privilege:
                if r.to_whom in principals:
                    if r.allow_or_deny == 'Allow':
                        return True
                    if r.allow_or_deny == 'Deny':
                        return False
        
        msg = 'Permission %r denied for %s' % (privilege, principals)
        msg += '\n' + indent('\n'.join(str(_) for _ in self.rules), '  ')
        logger.debug(msg)
        return False 

    def __str__(self):
        return str(self.rules)

@contract(x='list(list[3](str))')
def acl_from_yaml(x):
    '''

        Authenticated
        Everyone
        groups:<groupname>
        groups:admin
        groups:friends:andrea
        
        discover
        read
        write
        admin: change permissions
         
    '''
    rules = []
    for y in x:
        allow_or_deny = y[0]
        to_whom = y[1]
        privilege = y[2]
        if not privilege in PRIVILEGES:
            raise ValueError('Unknown privilege %r' % privilege)
        if privilege == PRIVILEGE_ALL:
            for p in PRIVILEGES:
                if p == PRIVILEGE_ALL: continue
                r = ACLRule(allow_or_deny=allow_or_deny, to_whom=to_whom, privilege=p)
                rules.append(r)
        else:
            r = ACLRule(allow_or_deny=allow_or_deny, to_whom=to_whom, privilege=privilege)
            rules.append(r)
    return ACL(rules) 
    