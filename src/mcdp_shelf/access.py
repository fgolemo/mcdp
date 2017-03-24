# -*- coding: utf-8 -*-
from collections import namedtuple

from contracts import contract
from contracts.utils import indent, raise_desc
from pyramid.security import Allow, Authenticated, Everyone, Deny

from mcdp.logs import logger_access
from mcdp.constants import MCDPConstants

Privileges = MCDPConstants.Privileges

USER_ANONYMOUS = 'anonymous'
# todo: change this to system.Authenticated
# todo: change this to system.Everyone
USER_AUTHENTICATED = 'Authenticated'
USER_EVERYONE = 'Everyone' 

ACLRule = namedtuple('ACLRule', 'allow_or_deny to_whom privilege')

class ACL():
    def __init__(self, rules):
        self.rules = rules
        
        
    def as_pyramid_acl(self):
        res = []
        for r in self.rules:
            a = {'Allow': Allow, 'Deny': Deny}[r.allow_or_deny]
            b = {USER_EVERYONE: Everyone, USER_AUTHENTICATED: Authenticated}.get(r.to_whom, r.to_whom)
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
                principals.append('group:%s'%g)
        
        return self.allowed_(privilege, principals)
    
    def allowed_(self, privilege, principals):
        if not privilege in Privileges.ALL_PRIVILEGES:
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
        logger_access.debug(msg)
        return False 

    def __str__(self):
        return str(self.rules)

@contract(x='list(list[3](str))')
def acl_from_yaml(x):
    '''

        Authenticated
        Everyone
        group:<groupname>
        group:admin
        group:friends:andrea
        
        discover
        read
        write
        admin: change permissions
         
    '''
    rules = []
    for y in x:
        allow_or_deny = y[0]
        to_whom = y[1]
        if to_whom.startswith('groups:'):
            msg = 'Invalid key "%s" - should be "group:...".' % to_whom
            raise_desc(ValueError, msg, x=x)
        
        privilege = y[2]
        if not privilege in Privileges.ALL_PRIVILEGES:
            raise ValueError('Unknown privilege %r' % privilege)
        if privilege == Privileges.SPECIAL_ALL_WILDCARD:
            for p in Privileges.ALL_PRIVILEGES:
                if p == Privileges.SPECIAL_ALL_WILDCARD: continue
                r = ACLRule(allow_or_deny=allow_or_deny, to_whom=to_whom, privilege=p)
                rules.append(r)
        else:
            r = ACLRule(allow_or_deny=allow_or_deny, to_whom=to_whom, privilege=privilege)
            rules.append(r)
    return ACL(rules) 
    