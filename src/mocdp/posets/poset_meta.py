from .space_meta import decorate_methods, SpaceMeta

__all__ = ['PosetMeta']

class PosetMeta(SpaceMeta):
    # we use __init__ rather than __new__ here because we want
    # to modify attributes of the class *after* they have been
    # created
    def __init__(cls, name, bases, dct):  # @NoSelf
        SpaceMeta.__init__(cls, name, bases, dct)

        methods2dec = {
            'join': join_decorator,
        }
        decorate_methods(cls, name, bases, dct, methods2dec)


def join_decorator(f):
    def join(self, a, b):
        try:
            self.belongs(a)
            self.belongs(b)
    
            res = f(self, a, b)
            
            self.belongs(res)
        except:
            print('Error while joining (%s, %s)' % (a, b))  # xxx
            raise

    return join

