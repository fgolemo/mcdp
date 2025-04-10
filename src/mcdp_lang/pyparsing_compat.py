# -*- coding: utf-8 -*-
"""
Compatibility layer between the bundled pyparsing_bundled.py (based on pyparsing 2.x)
and modern pyparsing 3.x.

This module should be used in place of direct imports from pyparsing_bundled.py.
It handles API differences between pyparsing 2.x and 3.x and ensures compatibility
with Python 3.
"""
import sys
from typing import Union, List, Optional as Opt, Callable, Any, Tuple

# Try to import from installed pyparsing 3.x
try:
    import pyparsing as pp
    # Import all classes that are currently used in the codebase
    from pyparsing import (
        # Parser Elements
        ParserElement, ParseExpression, ParseException, ParseFatalException,
        # Core parser elements
        Literal, CaselessLiteral, Keyword, Word, Combine, Optional, 
        NotAny, FollowedBy, OneOrMore, ZeroOrMore, Group, MatchFirst,
        Forward, QuotedString, Suppress,
        # Character sets
        alphas, alphanums, nums,
        # Quoted strings
        dblQuotedString, sglQuotedString, quotedString,
        # Other utilities
        opAssoc, operatorPrecedence,
    )
    
    # Check if we've got pyparsing 3.x
    is_pyparsing3 = int(pp.__version__.split('.')[0]) >= 3
except ImportError:
    # Fallback to bundled version if pyparsing 3.x is not installed
    from .pyparsing_bundled import (
        ParserElement, ParseExpression, ParseException, ParseFatalException,
        Literal, CaselessLiteral, Keyword, Word, Combine, Optional,
        NotAny, FollowedBy, OneOrMore, ZeroOrMore, Group, MatchFirst,
        Forward, QuotedString, Suppress,
        alphas, alphanums, nums,
        dblQuotedString, sglQuotedString, quotedString,
        opAssoc, operatorPrecedence,
    )
    is_pyparsing3 = False

# Import from mcdp's Python compatibility layer
from mcdp.py_compatibility import ensure_str, string_types, raise_with_traceback


# Ensure Parser Elements are properly configured
ParserElement.enablePackrat()


# Define the oneOf function with proper string/bytes handling
def oneOf(symbols, caseless=False, asKeyword=False):
    """
    Compatibility version of oneOf that handles string/bytes conversion properly.
    
    Parameters:
        symbols: Either a string of space-delimited symbols, or a list of symbols
        caseless: Whether to match symbols case-insensitively
        asKeyword: Whether to match symbols as keywords (only used in pyparsing 3.x)
    
    Returns:
        A MatchFirst of the symbols
    """
    if isinstance(symbols, string_types):
        symbols = symbols.split()
    
    # Ensure all symbols are proper strings
    symbols = [ensure_str(sym) for sym in symbols]
    
    if is_pyparsing3:
        # In pyparsing 3.x, the method is one_of and it accepts as_keyword
        return pp.one_of(symbols, caseless=caseless, as_keyword=asKeyword)
    else:
        # Use the bundled version which doesn't have asKeyword parameter
        from .pyparsing_bundled import oneOf as bundled_oneOf
        
        # If asKeyword is True and we're using the bundled version, we need to
        # manually implement keyword-like behavior by adding word boundaries
        if asKeyword:
            # Get each symbol as a Keyword instead (which ensures word boundaries)
            from .pyparsing_bundled import Keyword
            keywords = [Keyword(sym, caseless=caseless) for sym in symbols]
            # Use MatchFirst to create a choice between all keywords
            from .pyparsing_bundled import MatchFirst
            return MatchFirst(keywords)
        else:
            # Standard behavior without keyword requirement
            return bundled_oneOf(symbols, caseless=caseless)


# Add compatibility functions and methods
def parse_string(parser, text, parse_all=False):
    """
    Compatibility function for parseString/parse_string.
    
    Parameters:
        parser: The parser to use
        text: The text to parse
        parse_all: Whether to require the entire input string to be parsed
    
    Returns:
        The parse results
    """
    # Ensure text is a string
    text = ensure_str(text)
    
    if is_pyparsing3:
        return parser.parse_string(text, parse_all=parse_all)
    else:
        return parser.parseString(text, parseAll=parse_all)

def set_name(parser, name):
    """
    Compatibility function for setName/set_name.
    
    Parameters:
        parser: The parser to name
        name: The name to set
    
    Returns:
        The parser (for chaining)
    """
    if is_pyparsing3:
        return parser.set_name(name)
    else:
        return parser.setName(name)

def set_results_name(parser, name, list_all_matches=False):
    """
    Compatibility function for setResultsName/set_results_name.
    
    Parameters:
        parser: The parser to name
        name: The results name to set
        list_all_matches: Whether to list all matches
    
    Returns:
        The parser (for chaining)
    """
    if is_pyparsing3:
        return parser.set_results_name(name, list_all_matches=list_all_matches)
    else:
        return parser.setResultsName(name, listAllMatches=list_all_matches)

def set_parse_action(parser, *fns):
    """
    Compatibility function for setParseAction/set_parse_action.
    
    Parameters:
        parser: The parser to set the action on
        *fns: The parse actions to set
    
    Returns:
        The parser (for chaining)
    """
    if is_pyparsing3:
        return parser.set_parse_action(*fns)
    else:
        return parser.setParseAction(*fns)

def set_break(parser, break_flag=True):
    """
    Compatibility function for setBreak/set_break.
    
    Parameters:
        parser: The parser to set the break on
        break_flag: Whether to break
    
    Returns:
        The parser (for chaining)
    """
    if is_pyparsing3:
        return parser.set_break(break_flag)
    else:
        return parser.setBreak(break_flag)

# Add ParseResults compatibility methods
if is_pyparsing3:
    # Add backward compatibility methods to ParseResults
    original_init = pp.ParseResults.__init__
    
    def parse_results_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        
        # Add camelCase aliases for snake_case methods
        self.asDict = self.as_dict
        self.asList = self.as_list
        self.asXML = lambda: f"<ParseResults>{str(self)}</ParseResults>"
        
    pp.ParseResults.__init__ = parse_results_init


# Export all names so they can be easily imported
__all__ = [
    # Parser Elements
    'ParserElement', 'ParseExpression', 'ParseException', 'ParseFatalException',
    # Core parser elements
    'Literal', 'CaselessLiteral', 'Keyword', 'Word', 'Combine', 'Optional',
    'NotAny', 'FollowedBy', 'OneOrMore', 'ZeroOrMore', 'Group', 'MatchFirst',
    'Forward', 'QuotedString', 'Suppress',
    # Character sets
    'alphas', 'alphanums', 'nums',
    # Quoted strings
    'dblQuotedString', 'sglQuotedString', 'quotedString',
    # Other utilities
    'opAssoc', 'operatorPrecedence', 'oneOf', 
    # Compatibility helper functions
    'parse_string', 'set_name', 'set_results_name', 'set_parse_action', 'set_break',
]