from contracts import contract
from contracts.utils import raise_wrapped, indent

from mcdp import MCDPConstants
from mcdp_hdb.memdataview import ViewBytes
from mcdp_hdb.schema import NotValid
from mcdp_utils_misc.my_yaml import yaml_dump

from .memdataview import ViewContext0, ViewHash0, ViewList0, ViewString, ViewDate
from .memdataview_utils import host_name
from .schema import SchemaBase, SchemaContext, SchemaString, SchemaHash, SchemaList,  SchemaDate, SchemaBytes


__all__ = [
    'ViewManager',       
]

class ViewManager(object):
    '''
        A class that knows how to create views.
        
        You can register handler classes:
        
            class UserInfo(object):
                def get_email_long(self):
                    name = self.name
                    email = self.email
                    return '%s <%s>'.format(name, email)
                    
            vm = ViewManager(schema)
            vm.set_view_class(user, UserInfo)
            
            data = {'users': [ {'name':'andrea', 'email':'email'} ] }
            view = vm.view(data)
            
            user_info = view.users[0]

        Each view class contains a reference to a ViewManager.
    '''
    
    @contract(schema=SchemaBase)
    def __init__(self, schema):
        self.schema = schema

        self.s2baseclass = {}

    def set_view_class(self, s, baseclass):
        self.s2baseclass[s] = baseclass

    def view(self, data, actor=None, principals=None, host=None, inst_name=None):
        v = self.create_view_instance(self.schema, data)
        if actor is None:
            actor = 'system'
        if principals is None:
            principals = [MCDPConstants.ROOT]
        if host is None:
            host = host_name()
        v._who = {'host': host, 'actor': actor, 'inst_name': inst_name} #, 'principals': principals}
        v._principals = principals
    
        # create notify callback that saves everything to a .events
        # variable
        v._events = []    
        def notify_callback(event):
            v._events.append(event)
        v._notify_callback = notify_callback
        return v

    @contract(s=SchemaBase)
    def create_view_instance(self, s, data):
        try:
            s.validate(data)
        except NotValid as e:
            msg = 'Could not create view instance because the data is not valid '
            msg += 'according to the schema.'
            msg += '\n' + indent(s.__str__(), 'schema: ')
            msg += '\n' + indent(yaml_dump(data), 'data: ')
            raise_wrapped(NotValid, e, msg, compact=True) 
        if s in self.s2baseclass:
            class Base(self.s2baseclass[s]):
                pass
        else:
            class Base(object):
                pass

        if isinstance(s, SchemaContext):
            class ViewContext(ViewContext0, Base): 
                pass
            try:
                view = ViewContext(view_manager=self, data=data, schema=s)
                view.init_context()
                return view
            except TypeError as e:
                msg = 'Probably due to a constructor in Base = %s' % (Base)
                if s in self.s2baseclass:
                    msg += '\n' + str(self.s2baseclass[s])
                raise_wrapped(ValueError, e, msg)

        if isinstance(s, SchemaHash):
            class ViewHash(ViewHash0, Base): 
                pass
            view = ViewHash(view_manager=self, data=data, schema=s)
            view.init_hash()
            return view
        
        if isinstance(s, SchemaList):
            class ViewList(ViewList0, Base): 
                pass
            return ViewList(view_manager=self, data=data, schema=s)
    
        if isinstance(s, SchemaString):
            return ViewString(view_manager=self, data=data, schema=s)

        if isinstance(s, SchemaBytes):
            return ViewBytes(view_manager=self, data=data, schema=s)
        
        if isinstance(s, SchemaDate):
            return ViewDate(view_manager=self, data=data, schema=s)
        
        raise NotImplementedError(type(s))
