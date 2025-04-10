# -*- coding: utf-8 -*-
# Use io.StringIO for Python 3
try:
    # Python 2
    from StringIO import StringIO
except ImportError:
    # Python 3
    from io import StringIO

# Handle pickle imports for Python 3
import pickle
from pickle import (Pickler, SETITEM, MARK, SETITEMS, EMPTY_TUPLE, TUPLE, POP, POP_MARK)
# _tuplesize2code is a private attribute in pickle, which may not be available in Python 3
# Create a fallback if it's not available
try:
    from pickle import _tuplesize2code
except ImportError:
    # Simple fallback that works for the common cases
    _tuplesize2code = {1: pickle.TUPLE1, 2: pickle.TUPLE2, 3: pickle.TUPLE3}

import traceback

# Import describe_type directly from contracts
from contracts.interface import describe_type

from mcdp import logger


def find_pickling_error(obj, protocol=pickle.HIGHEST_PROTOCOL):
    sio = StringIO()
    try:
        pickle.dumps(obj)
    except Exception as e1:
        # s1 = traceback.format_exc(e1)
        pass
    else:
        msg = ('Strange! I could not reproduce the pickling error '
                f"for the object of class {describe_type(obj)}")
        logger.info(msg)

    pickler = MyPickler(sio, protocol)
    try:
        pickler.dump(obj)
    except Exception as e1:
        msg = pickler.get_stack_description()
        msg += f"\n --- Current exception----\n{traceback}".format_exc(e1)
        msg += f"\n --- Old exception----\n{traceback}".format_exc(e1)
        return msg
    else:
        msg = 'I could not find the exact pickling error.'
        raise Exception(msg)


class MyPickler(Pickler):
    def __init__(self, *args, **kargs):
        Pickler.__init__(self, *args, **kargs)
        self.stack = []

    def save(self, obj):
        desc = f"object of type {describe_type(obj)}"
        # , describe_value(obj, 100))
        #  self.stack.append(describe_value(obj, 120))
        self.stack.append(desc)
        Pickler.save(self, obj)
        self.stack.pop()

    def get_stack_description(self):
        s = 'Pickling error occurred at:\n'
        for i, context in enumerate(self.stack):
            s += f" ' * i + '- {context}\n"
        return s

    def save_pair(self, k, v):
        self.stack.append(f"key {k!r} = object of type {type(k)}")
        self.save(k)
        self.save(v)
        self.stack.pop()

    def _batch_setitems(self, items):

        # Helper to batch up SETITEMS sequences; proto >= 1 only
        # save = self.save
        write = self.write

        if not self.bin:
            for k, v in items:
                self.stack.append(f"entry {str(k)}")
                self.save_pair(k, v)
                self.stack.pop()
                write(SETITEM)
            return

        # Use range in Python 3, xrange in Python 2
        try:
            r = xrange(self._BATCHSIZE)  # Python 2
        except NameError:
            r = range(self._BATCHSIZE)  # Python 3
        while items is not None:
            tmp = []
            for _ in r:
                try:
                    # In Python 3, .next() was renamed to __next__()
                    if hasattr(items, 'next'):
                        # Python 2
                        tmp.append(items.next())
                    else:
                        # Python 3
                        tmp.append(next(items))
                except StopIteration:
                    items = None
                    break
            n = len(tmp)
            if n > 1:
                write(MARK)
                for k, v in tmp:
                    self.stack.append(f"entry {str(k)}")
                    self.save_pair(k, v)
                    self.stack.pop()
                write(SETITEMS)
            elif n:
                k, v = tmp[0]
                self.stack.append(f"entry {str(k)}")
                self.save_pair(k, v)
                self.stack.pop()
                write(SETITEM)
            # else tmp is empty, and we're done


    def save_tuple(self, obj):
        write = self.write
        proto = self.proto

        n = len(obj)
        if n == 0:
            if proto:
                write(EMPTY_TUPLE)
            else:
                write(MARK + TUPLE)
            return

        save = self.save
        memo = self.memo
        if n <= 3 and proto >= 2:
            for i, element in enumerate(obj):
                self.stack.append(f"tuple element {i}")
                save(element)
                self.stack.pop()
            # Subtle.  Same as in the big comment below.
            if id(obj) in memo:
                get = self.get(memo[id(obj)][0])
                write(POP * n + get)
            else:
                write(_tuplesize2code[n])
                self.memoize(obj)
            return

        # proto 0 or proto 1 and tuple isn't empty, or proto > 1 and tuple
        # has more than 3 elements.
        write(MARK)
        for i, element in enumerate(obj):
            self.stack.append(f"tuple element {i}")
            save(element)
            self.stack.pop()

        if id(obj) in memo:
            # Subtle.  d was not in memo when we entered save_tuple(), so
            # the process of saving the tuple's elements must have saved
            # the tuple itself:  the tuple is recursive.  The proper action
            # now is to throw away everything we put on the stack, and
            # simply GET the tuple (it's already constructed).  This check
            # could have been done in the "for element" loop instead, but
            # recursive tuples are a rare thing.
            get = self.get(memo[id(obj)][0])
            if proto:
                write(POP_MARK + get)
            else:  # proto 0 -- POP_MARK not available
                write(POP * (n + 1) + get)
            return

        # No recursion.
        self.write(TUPLE)
        self.memoize(obj)
