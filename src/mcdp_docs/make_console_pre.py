# -*- coding: utf-8 -*-
from bs4.element import NavigableString, Tag

from mcdp_utils_xml import bs, to_html_stripping_fragment



def mark_console_pres(soup):    
    for code in soup.select('pre code'):
        pre = code.parent
        if code.string is None:
            continue
        s0 = code.string
        
        from HTMLParser import HTMLParser
        h = HTMLParser()
        s = h.unescape(s0)
        if s != s0:
#             print('decoded %r -> %r' % (s0, s))
            pass  
        
        beg = s.strip()
        if beg.startswith('DOLLAR') or beg.startswith('$'):
            pass
#             print('it is console (%r)' % s)
        else:
#             print('not console (%r)' % s)
            continue

        from mcdp_docs.highlight import add_class
        add_class(pre, 'console')

        code.string = ''
        
        lines = s.split('\n')
        
        programs = ['sudo', 'pip', 'git', 'python', 'cd', 'apt-get',
                    'mcdp-web', 'mcdp-solve', 'mcdp-render', 'npm',
                    'mcdp-plot','mcdp-eval','mcdp-render-manual']
        program_commands = ['install', 'develop', 'clone']
        
        def is_program(x, l):
            if x == 'git' and 'apt-get' in l:
                return False
            return x in programs
            
        for j, line in enumerate(lines):
            tokens = line.split(' ')
            for i, token in enumerate(tokens):
                if token in  ['$', 'DOLLAR']:
                    # add <span class=console_sign>$</span>
                    e = Tag(name='span')
                    e['class'] = 'console_sign'
                    e.string = '$'
                    code.append(e)
                elif is_program(token, line):
                    e = Tag(name='span')
                    e['class'] = '%s program' % token
                    e.string = token
                    code.append(e)
                elif token in program_commands:
                    e = Tag(name='span')
                    e['class'] = '%s program_command' % token
                    e.string = token
                    code.append(e)
                elif token and token[0] == '-':
                    e = Tag(name='span')
                    e['class'] = 'program_option'
                    e.string = token
                    code.append(e)
                else:
                    code.append(NavigableString(token))
                    
                is_last = i == len(tokens) - 1
                if not is_last:
                    code.append(NavigableString(' '))
            
            is_last_line = j == len(lines) - 1
            if not is_last_line:
                code.append(NavigableString('\n'))
 