from mcdp.exceptions import DPSemanticError
from mcdp import logger
from mcdp.constants import MCDPConstants
from mcdp_lang.parse_actions import parse_wrap
from mcdp_library.specs_def import specs
from mcdp_utils_misc.string_utils import format_list

from contracts.utils import raise_desc
import time


class HostCache(object):
    
    def __init__(self, db_view):
        self.db_view = db_view
        # key = (spec_name, source)
        self.parsing_cache = {} # key -> namedtuplewhere
        self.parsing_cache_time_ms = {} # key -> ms
        # key = (repo_name, shelf_name, library_name, spec_name, thing_name)
        self.evaluated= {}
        
    def load_spec(self, repo_name, shelf_name, library_name, spec_name, thing_name, context):
        db_view = self.db_view
        
        key0 = (repo_name, shelf_name, library_name, spec_name, thing_name)
        if not key0 in self.evaluated:
            x = get_source(db_view, repo_name, shelf_name, library_name, spec_name, thing_name)
            source = x['data']
            # We can do the parsing only once. It only depends on the string 
            # and nothing else
            key = (spec_name, source)
            if not key in self.parsing_cache:
                t0 = time.clock()
                self.parsing_cache[key] = \
                    self.parse_source(spec_name, source, context)
                t1 = time.clock()
                dms = 1000 * (t1-t0)
                self.parsing_cache_time_ms[key] = dms
                logger.warn('Parsing %s: %s ms' % (thing_name, dms))
            else:
                dms =  self.parsing_cache_time_ms[key]
                logger.debug('Parsing %s: saved %s' % (thing_name, dms))
                
            parsed = self.parsing_cache[key] 
            
            parse_eval = specs[spec_name].parse_eval
            res = parse_eval(parsed, context)
            self.evaluated[key0] = res
        
        return self.evaluated[key0]
        
        
    def parse_source(self, spec_name, source, context):
        parse_expr = specs[spec_name].parse_expr
        parse_refine = specs[spec_name].parse_refine
        # Here we parse and refine
        expr = parse_wrap(parse_expr, source)[0]
        expr2 = parse_refine(expr, context)
        return expr2

def get_source(db_view, repo_name, shelf_name, library_name, spec_name, thing_name):
    
    from mcdp_hdb_mcdp.library_view import get_soft_match
    shelf = db_view.repos[repo_name].shelves[shelf_name]
    library = shelf.libraries[library_name]
    things = library.things.child(spec_name)
    
    try:
        match = get_soft_match(thing_name, list(things))
    except KeyError:
        msg = 'Soft match failed: Could not find %r in %s.' % (thing_name, spec_name)
        available = sorted(things)

        if available:
            msg += ("\n Available %s: %s." % (spec_name, format_list(sorted(available))))
        else:
            msg += "\n None available."
        
        raise_desc(DPSemanticError, msg)
    else:
        
        if match != thing_name:
            if MCDPConstants.allow_soft_matching:
                logger.warning('Soft matching %r to %r (deprecated)' % (match, thing_name))
            else:
                msg = 'Found case in which the user relies on soft matching (%r to refer to %r).' % (thing_name, match)
                raise DPSemanticError(msg)
            # TODO: add warning 
            
        data = things[match]
        spec = specs[spec_name]
        basename  = match + '.' + spec.extension
        realpath = ('%s in library %r in shelf %r in repo %r' % 
                    (basename, library_name, shelf_name, repo_name)) 
        return dict(data=data, realpath=realpath)
    
    