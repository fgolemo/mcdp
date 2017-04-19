# -*- coding: utf-8 -*- 
from contracts import contract
from contracts.utils import indent
from pyramid.security import Allow, Authenticated, Everyone, Deny

from mcdp.constants import MCDPConstants
from mcdp.logs import logger_access, logger

Privileges = MCDPConstants.Privileges

class ACLRule(object):
    
    def __init__(self, allow_or_deny, to_whom, privilege):
        self.allow_or_deny = allow_or_deny
        self.to_whom = to_whom
        self.privilege = privilege
        
        if not privilege in Privileges.ALL_PRIVILEGES:
            raise ValueError('Unknown privilege %r' % privilege) 
            
        def valid_group(x):
            return len(x) > 0
        def valid_username(x):
            return len(x) > 0
        valid = False
        some_ok = [
            MCDPConstants.EVERYONE, 
            MCDPConstants.AUTHENTICATED,
        ] 
        if to_whom in some_ok: 
            valid = True  
        elif to_whom.startswith('user:'):
            username = to_whom[to_whom.index(':')+1:]
            valid = valid_username(username)
        elif to_whom.startswith('group:'):
            group = to_whom[to_whom.index(':')+1:]
            valid = valid_group(group)
        elif to_whom.startswith('special:'):
            valid = True
        else:
            pass
        if not valid:
            msg = 'Invalid to_whom spec: %s' % to_whom
            logger.error(msg)

    def as_pyramid_acl(self):
        a = {MCDPConstants.ALLOW: Allow, MCDPConstants.DENY: Deny}[self.allow_or_deny]
        d = {MCDPConstants.EVERYONE: Everyone, 
             MCDPConstants.AUTHENTICATED: Authenticated}
        b = d.get(self.to_whom, self.to_whom)
        c = self.privilege    
        if c == Privileges.SPECIAL_ALL_WILDCARD:
            c = tuple(Privileges.ALL_PRIVILEGES)
        return (a,b,c)
    
    def __repr__(self):
        return ('ACLRule(%s %s to %s)' % 
                (self.allow_or_deny, self.privilege, self.to_whom))

class ACL(object):
    def __init__(self, rules):
        self.rules = rules
        
    def as_pyramid_acl(self):
        root_rule = (Allow, MCDPConstants.ROOT, tuple(Privileges.ALL_PRIVILEGES))
        rules = map(ACLRule.as_pyramid_acl, self.rules)
        return [root_rule] + rules
        
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
        
        # We grant root all privileges
        if MCDPConstants.ROOT in principals:
            return True
        
        for r in self.rules:
            matches = ((r.privilege == Privileges.SPECIAL_ALL_WILDCARD) or
                       (r.privilege==privilege))
            
            if not matches: continue
            
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
    rules = []
    for y in x:
        allow_or_deny = y[0]
        to_whom = y[1]
        privilege = y[2] 
#         if privilege == Privileges.SPECIAL_ALL_WILDCARD:
#             for p in Privileges.ALL_PRIVILEGES:
#                 if p == Privileges.SPECIAL_ALL_WILDCARD: continue
#                 r = ACLRule(allow_or_deny, to_whom, p)
#                 rules.append(r)
#         else:
        r = ACLRule(allow_or_deny, to_whom, privilege)
        rules.append(r)
    return ACL(rules) 
    