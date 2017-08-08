# -*- coding: utf-8 -*-
from bs4.element import NavigableString, Tag
from collections import namedtuple
from contracts import contract
from comptests.registrar import comptest, run_module_tests

ConsoleLine = namedtuple('ConsoleLine', 'hostname symbol command')

@contract(returns='$ConsoleLine|None')
def is_console_line(line):
    """ Returns true if it looks like a console line, such as:
    
        $ command args
        hostname $ command args
        hostname # command args
    """
    def is_console_token(x):
        return x in ['#', '$', 'DOLLAR']
    
    tokens = line.strip().split(' ')
    if not tokens: 
        return None
    if is_console_token(tokens[0]):
        hostname = None
        symbol = tokens[0] 
        command = " ".join(tokens[1:])
        
    elif len(tokens) >= 2 and is_console_token(tokens[1]):
        hostname = tokens[0]
        symbol = tokens[1]
        command = " ".join(tokens[2:])
        
    else:
        return None
    
    return ConsoleLine(hostname=hostname, symbol=symbol, command=command)

@comptest
def is_console_line_test():
    s = "laptop $ sudo dd of=DEVICE if=IMG status=progress bs=4M "
    ct = is_console_line(s)
    assert ct is not None
    assert ct.hostname == 'laptop'
    assert ct.symbol == '$'
    assert ct.command == 'sudo dd of=DEVICE if=IMG status=progress bs=4M'

    s = " # echo"
    ct = is_console_line(s)
    assert ct is not None
    assert ct.hostname == None
    assert ct.symbol == '#'
    assert ct.command == 'echo'
    
    s = " DOLLAR echo"
    ct = is_console_line(s)
    assert ct is not None
    assert ct.hostname == None
    assert ct.symbol == 'DOLLAR'
    assert ct.command == 'echo'

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
        
        
        ct = is_console_line(beg)
        
        if ct is None: 
            continue

        from mcdp_docs.highlight import add_class
        add_class(pre, 'console')

        code.string = ''
        
        lines = s.split('\n')
        
        programs = ['sudo', 'pip', 'git', 'python', 'cd', 'apt-get',
                    'mcdp-web', 'mcdp-solve', 'mcdp-render', 'npm',
                    'mcdp-plot','mcdp-eval','mcdp-render-manual',
                    'dd', 'apt', 'ifconfig', 'iconfig', 'htop',
                    'iotop', 'iwlist', 'git-ignore','sha256sum','umount', 'mount', 'xz',
                    'raspi-config', 'usermod', 'udevadm', 'sh', 'apt-key','systemctl',
                    'mkswap', 'swapon', 'visudo', 'update-alternatives',
                    'mkdir', 'chmod', 'wget', 'byobu-enable', 'exit','ssh','scp','rsync',
                    'raspistill', 'reboot', 'vim', 'vi', 'ping', 'ssh-keygen',
                    'mv', 'cat', 'touch' ,'source', 'make', 'roslaunch', 'jstest',
                    'shutdown', 'virtualenv', 'nodejs', 'cp', 'fc-cache', 'venv']
        program_commands = ['install', 'develop', 'clone', 'config']
        
        def is_program(x, l):
            if x == 'git' and 'apt' in l:
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


if __name__ == '__main__':
    run_module_tests()