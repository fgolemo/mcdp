from decorator import decorator

def memoize_simple(obj):
    cache = obj.cache = {}

    def memoizer(f, *args):
        key = (args)
        if key not in cache:
            cache[key] = f(*args)
            # print('memoize: %s %d storage' % (obj, len(cache)))
        return cache[key]

    return decorator(memoizer, obj)
