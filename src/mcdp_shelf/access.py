# -*- coding: utf-8 -*- 
from contracts import contract
from contracts.utils import indent, raise_desc
from pyramid.security import Allow, Authenticated, Everyone, Deny

from mcdp.logs import logger_access
from mcdp.constants import MCDPConstants

Privileges = MCDPConstants.Privileges

class ACLRule(object):
    
    def __init__(self, allow_or_deny, to_whom, privilege):
        self.allow_or_deny = allow_or_deny
        self.to_whom = to_whom
        self.privilege = privilege
        
        if not privilege in Privileges.ALL_PRIVILEGES:
            raise ValueError('Unknown privilege %r' % privilege)
        if privilege == Privileges.SPECIAL_ALL_WILDCARD:
            raise ValueError('Cannot use privilege %r' % privilege)

    def as_pyramid_acl(self):
        a = {MCDPConstants.ALLOW: Allow, MCDPConstants.DENY: Deny}[self.allow_or_deny]
        d = {MCDPConstants.EVERYONE: Everyone, MCDPConstants.AUTHENTICATED: Authenticated}
        b = d.get(self.to_whom, self.to_whom)
        c = self.privilege    
        return (a,b,c)
    
    def __repr__(self):
        return 'ACLRule(%s %s to %s)' % (self.allow_or_deny, self.privilege, self.to_whom)

class ACL(object):
    def __init__(self, rules):
        self.rules = rules
        
    def as_pyramid_acl(self):
        return map(ACLRule.as_pyramid_acl, self.rules)
        
    def allowed2(self, privilege, user):
        return self.allowed(privilege, user.username, user.groups)
    
    def allowed(self, privilege, username, groups):
        principals = []
        principals.append(MCDPConstants.EVERYONE)
        if username is not None and username != MCDPConstants.USER_ANONYMOUS:
            principals.append(MCDPConstants.AUTHENTICATED)
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
                    if r.allow_or_deny == MCDPConstants.ALLOW:
                        return True
                    elif r.allow_or_deny ==  MCDPConstants.DENY:
                        return False
                    else: 
                        assert False, r
        
        msg = 'Permission %r denied for %s' % (privilege, principals)
        msg += '\n' + indent('\n'.join(str(_) for _ in self.rules), '  ')
        logger_access.debug(msg)
        return False 

    def __str__(self):
        s = 'ACL('
        for r in self.rules:
            s += '\n %s' % r  
        s += '\n)'
        return s

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
                r = ACLRule(allow_or_deny, to_whom, p)
                rules.append(r)
        else:
            r = ACLRule(allow_or_deny, to_whom, privilege)
            rules.append(r)
    return ACL(rules) 
    