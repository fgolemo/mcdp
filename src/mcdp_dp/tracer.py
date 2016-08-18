from contracts import contract
from contextlib import contextmanager
from contracts.utils import indent, raise_desc


class TracerEvent():

    def format(self):
        raise NotImplementedError()


class Tracer():
    """ 
    
        This is a support class for logging the trace of a recursive
        operation.
       
           with t.child('dp1') as t2:
               solve(t2)
        
    """
    
    def __init__(self, prefix="", logger=None):
        """
            If logger is not None, the output is to the logger as well.
        """
        self.chronology = []
        self.prefix = prefix
        self.logger = logger

    def __repr__(self):
        return 'Tracer(%s)' % self.chronology

    def repr_long(self):
        return self.__repr__()

    def __getstate__(self):
        # do not pickle logger
        return dict(prefix=self.prefix, chronology=self.chronology)

    @contract(e=TracerEvent)
    def _log_event(self, e):
        self.chronology.append(e)
            
    def log(self, s):
        """ Records a string """
        if self.logger is not None:
            self.logger.info(self.prefix + s)
        self._log_event(TracerLog(s))
        
    @contextmanager
    def child(self, name):
        t = Tracer(prefix=self.prefix + ":" + name, logger=self.logger)
        yield t
        if t.chronology:
            last = t.chronology[-1]
            if isinstance(last, TracerResult):
                result = last.value
            else:
                result = None
        else:
            result = None
        self._log_event(TracerRecursion(name, t, result))
        
    @contextmanager
    def iteration(self, i):
        name = 'it%d' % i
        with self.child(name) as t:
            yield t
        
    def values(self, **args):
        for name, value in args.items():
            self._log_event(TracerValue(name, value))
    def value(self, name, value):
        self._log_event(TracerValue(name, value))
        
    def result(self, ob):
        """ Returns ob """
        self._log_event(TracerResult(ob))
        return ob
        
    def format(self):
        if not self.chronology:
            return '(empty)'
        fs = []
        for c in self.chronology:
            s = c.format()
            s = indent(s, '  ', first='- ')
            fs.append(s)
        return "\n".join(fs)

    # read interface
    def get_iterations(self):
        for x in self.chronology:
            if isinstance(x, TracerRecursion):
                yield x

    def find_loops(self):
        for x in self.rec_find_has_value('type', 'loop'):
            yield x

    def rec_find_has_value(self, name, value):
        if value in list(self.get_value(name)):
            yield self
        for x in self.chronology:
            if isinstance(x, TracerRecursion):
                for _ in x.trace.rec_find_has_value(name, value):
                    yield _

    def rec_get_value(self, name):
        values = list(self.get_value(name))
        for v in values:
            yield v

        for x in self.chronology:
            if isinstance(x, TracerRecursion):
                for _ in x.trace.rec_get_value(name):
                    yield _

    def get_iteration_values(self, name):
        iterations = self.get_iterations()
        for i in iterations:
            for _ in i.trace.get_value(name):
                yield _

    def get_value1(self, name):
        l = list(self.get_value(name))
        if len(l) > 1:
            msg = 'Multiple values found.'
            raise_desc(ValueError, msg, name=name, l=l)
        if not l:
            msg = 'No values found.'
            raise_desc(ValueError, msg, name=name)
        return l[0]

    def get_value(self, name):
        for x in self.chronology:
            if isinstance(x, TracerValue) and x.name == name:
                yield x.value

class TracerRecursion(TracerEvent):
    @contract(name='str', trace=Tracer)
    def __init__(self, name, trace, result):
        self.name = name
        self.trace = trace
        self.result = result

    def __repr__(self):
        return 'TracerRecursion(%s,%s,%s)' % (self.name, self.trace, self.result)

    def format(self):
        name = self.name
        start = '%s: ' % name
        fill = '|' + ' ' * (len(start) - 1)
        return indent(self.trace.format(), fill, start)

class TracerValue(TracerEvent):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return 'TracerValue(%s,%s)' % (self.name, self.value)

    def format(self):
        return '%s = %s' % (self.name, self.value)

class TracerResult(TracerValue):
    def __init__(self, value):
        TracerValue.__init__(self, 'return', value)
        
    def format(self):
        return 'return %s' % str(self.value)

class TracerLog(TracerEvent):
    @contract(s='str')
    def __init__(self, s):
        self.s = s
    def format(self):
        return self.s
