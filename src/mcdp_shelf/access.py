# -*- coding: utf-8 -*-
from contracts import contract
from collections import namedtuple

ACCESS_READ = 'read'
ACCESS_WRITE = 'write'
USER_ANONYMOUS = 'anonymous'

ACLRule = namedtuple('ACLRule', 'allow_or_deny to_whom privilege')

class ACL():
    def __init__(self, rules):
        self.rules = rules
        
    def allowed(self, privilege, username, groups):
        principals = []
        principals.append('Everyone')
        if username is not None:
            principals.append('Authenticated')
        if groups:
            for g in groups:
                principals.append('groups:%s'%g)
        return self.allowed_(privilege, principals)
    
    def allowed_(self, privilege, principals):
        for r in self.rules:
                if r.privilege == privilege:
                    if r.to_whom in principals:
                        if r.allow_or_deny == 'Allow':
                            return True
                        if r.allow_or_deny == 'Deny':
                            return False
        return False 
            
        
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
        r = ACLRule(allow_or_deny=allow_or_deny, to_whom=to_whom, privilege=privilege)
        rules.append(r)
    return ACL(rules) 
    