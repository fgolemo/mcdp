# -*- coding: utf-8 -*-
import re
import os
from contracts.utils import raise_desc, raise_wrapped, check_isinstance
from contracts.interface import Where
from mocdp.exceptions import DPSyntaxError


def latex_preprocessing(s):
    s = s.replace('~$', '&nbsp;$')
#     s = s.replace('{}', '') # cannot do - mcdp { }
    # note: nongreedy matching ("?" after *);
#     def fix(m):
#         x=m.group(1)
#         if not 'eq:' in x:
#             print('fixing %r to eq:%s' % (x, x))
#             x = 'eq:' + x
#         return '\\eqref{%s}' %x
    
    # note: thi
    group = 'TILDETILDETILDE'
    s = s.replace('~~~', group)
    s = s.replace('~', ' ') # XXX
    s = s.replace(group, '~~~')
    
    s = re.sub(r'\\textendash\s*', '&ndash;', s) # XXX
    s = re.sub(r'\\textemdash\s*', '&mdash;', s) # XXX
     
    
    s = re.sub(r'\\noindent\s*', '', s) # XXX
# {[}m{]}}, and we need to choose the \R{endurance~$T$~{[}s{]}}
    s = re.sub(r'{(\[|\])}', r'\1', s)
#     s = re.sub(r'\\R{(.*?)}', r'<r>\1</r>', s)
#     s = re.sub(r'\\F{(.*?)}', r'<f>\1</f>', s)
#     

    # no! let mathjax do it
    def subit(m):
        x = m.group(1)
        if x.startswith('eq:'):
            return '\\ref{%s}' % x
        else:
            return '<a href="#\1"></a>'
    s = re.sub(r'\\ref{(.*?)}', subit, s)
    
    s = re.sub(r'\\eqref{(.*?)}', r'\\eqref{eq:\1}', s)
    s = s.replace('eq:eq:', 'eq:')
    
    # \vref
    s = re.sub(r'\\vref{(.*?)}', r'<a class="only-number" href="#\1"></a>', s)
       
    
#     s = re.sub(r'\\eqref{(.*?)}', r'<a href="#eq:\1"></a>', s)
    
    s = re.sub(r'\\lemref{(.*?)}', r'<a href="#lem:\1"></a>', s)
    s = re.sub(r'\\tabref{(.*?)}', r'<a href="#tab:\1"></a>', s)
    s = re.sub(r'\\figref{(.*?)}', r'<a href="#fig:\1"></a>', s)
    s = re.sub(r'\\proref{(.*?)}', r'<a href="#pro:\1"></a>', s)
    s = re.sub(r'\\propref{(.*?)}', r'<a href="#prop:\1"></a>', s)
    s = re.sub(r'\\probref{(.*?)}', r'<a href="#prob:\1"></a>', s)
    s = re.sub(r'\\defref{(.*?)}', r'<a href="#def:\1"></a>', s)
    s = re.sub(r'\\exaref{(.*?)}', r'<a href="#exa:\1"></a>', s)
    s = re.sub(r'\\secref{(.*?)}', r'<a href="#sec:\1"></a>', s)
    
    s = sub_headers(s)               
    s = re.sub(r'\\cite\[(.*)?\]{(.*?)}', r'<cite id="\2">[\1]</cite>', s)
    s = re.sub(r'\\cite{(.*?)}', r'<cite id="\1" replace="true">[\1]</cite>', s)
    
    # note: nongreedy matching ("?" after *); and multiline (re.M) DOTALL = '\n' part of .
    s = re.sub(r'\\emph{(.*?)}', r'<em>\1</em>', s, flags=re.M | re.DOTALL)
    s = re.sub(r'\\textbf{(.*?)}', r'<strong>\1</strong>', s, flags=re.M | re.DOTALL)
    s = s.replace('~"', '&nbsp;&ldquo;')
    s = s.replace('\,', '&ensp;')
    s = s.replace('%\n', '\n')
    
    s = substitute_simple(s, 'etal', 'et. al.')

    s = replace_includegraphics(s)
    s = substitute_command(s, 'fbox', lambda name, inside: 
                           '<div class="fbox">' + inside + "</div>" )
    s = substitute_simple(s, 'scottcontinuity', 'Scott continuity')
    s = substitute_simple(s, 'scottcontinuous', 'Scott continuous')
    
    s = substitute_simple(s, 'hfill', '')
    s = substitute_simple(s, 'centering', '')
    s = substitute_simple(s, 'medskip', '')
    s = substitute_simple(s, 'par', '<br class="from_latex_par"/>')
    s = replace_captionsideleft(s)
    
    s = substitute_command(s, 'F', lambda name, inside: '<span class="Fcolor">%s</span>' % inside)
    s = substitute_command(s, 'R', lambda name, inside: '<span class="Rcolor">%s</span>' % inside)
    s = substitute_command(s, 'uline', lambda name, inside: '<span class="uline">%s</span>' % inside)

    for x in ['footnotesize', 'small']:
        s = substitute_command(s, x, 
                               lambda name, inside: '<span class="apply-parent %s">%s</span>' % (x, inside))

    s = replace_environment(s, "defn", "definition", "def:")
    s = replace_environment(s, "lem", "lemma", "lem:")
    s = replace_environment(s, "rem", "remark", "rem:")
    s = replace_environment(s, "thm", "thorem", "thm:")
    s = replace_environment(s, "prop", "proposition", ("pro:", "prop:"))
    s = replace_environment(s, "example", "example", "exa:")
    s = replace_environment(s, "proof", "proof", "proof:")
    s = replace_environment(s, "problem", "problem", "prob:")
    s = replace_environment(s, "abstract", "abstract", None)
    s = replace_environment(s, "centering", "centering", None)
    
    
    s = replace_environment_ext(s, "figure", lambda inside, opt: makefigure(inside, opt, False))
    s = replace_environment_ext(s, "figure*",lambda inside, opt: makefigure(inside, opt, True))
    
    s = s.replace('pro:', 'prop:')
    
    s = replace_quotes(s)
#     if 'defn' in s:
#         raise ValueError(s)
    return s

def makefigure(inside, opt, asterisk):
    align = opt  # @UnusedVariable
    print('makefigure inside = %r'  % inside)
    def subfloat_replace(args, opts):
        contents = args[0]
        caption = opts[0]
        if caption is None: caption = 'no subfloat caption'
        res = '<figure>%s<figcaption>%s</figcaption></figure>' % (contents, caption)
        return res
    
    inside = substitute_command_ext(inside, 'subfloat', subfloat_replace, nargs=1, nopt=1)
#     print('makefigure inside now = %r'  % inside)
    class Tmp:
        label = None
    
    def sub_caption(args, opts):
        assert not opts and len(args) == 1
#         print('caption xargs = %s' % args.__repr__())
        x, Tmp.label = get_s_without_label(args[0], labelprefix="fig:")
#         print('caption x = %s' % x.__repr__())
        res = '<figcaption>' + x + "</figcaption>" 
        return res
    
    inside = substitute_command_ext(inside, 'caption', sub_caption, nargs=1, nopt=0)
    
    if Tmp.label is not None:
        idpart = ' id="%s"' % Tmp.label
    else:
        idpart = ""

    res  = '<figure%s>%s</figure>' % (idpart, inside)
    return res

def sub_headers(s):
    def sub_header(ss, cmd, hname, number=True):
        def replace(name, inside):  # @UnusedVariable
            options = ""
            options += ' nonumber' if number is False else ''
            inside, label = get_s_without_label(inside, labelprefix=None)
            options += ' id="%s"' % label if label is not None else ''
            template = '<{hname}{options}>{inside}</{hname}>' 
            r = template.format(hname=hname, inside=inside, options=options)
            return r
        return substitute_command(ss, cmd, replace)
    
    # note that we need to do the * version before the others
    s = sub_header(s, cmd='section*', hname='h1', number=False)
    s = sub_header(s, cmd='section', hname='h1', number=True)
    s = sub_header(s, cmd='subsection*', hname='h2', number=False)
    s = sub_header(s, cmd='subsection', hname='h2', number=True)
    s = sub_header(s, cmd='subsubsection*', hname='h3', number=False)
    s = sub_header(s, cmd='subsubsection', hname='h3', number=True)
    return s
  
def substitute_simple(s, name, replace):
    """
        \ciao material-> submaterial
        \ciao{} material -> submaterial
    """
    print(len(s))
    
    start = '\\' + name
    if not start in s:
        return s
    
    # points to the '{'
    istart = s.index(start)
    i = istart + len(start)
    
    next_char = s[i+1] 
    
    # don't match '\ciao' when looking for '\c'
    is_match = not next_char.isalpha()
    if not is_match:
        return s[:i] + substitute_simple(s[i:], name, replace) 


    after0 = s[i:]
    eat_space = True
    if len(after0)> 2 and after0[:2] == '{}':
        eat_space = False
            
    if eat_space:
        while i < len(s) and (s[i] in [' ']):
            i += 1
    after = s[i:]
    
    before = s[:istart] 
    return before + replace + substitute_simple(after, name, replace)
    
    
    
class Malformed(Exception):
    pass

def substitute_command_ext(s, name, f, nargs, nopt):
    """
        Subsitute \name[x]{y}{z} with 
        f : args=(x, y), opts=None -> s
        if nargs=1 and nopt = 0:
            f : x -> s
    """
    lookfor = '\\' + name + '[' if nopt > 0 else '{'
    
    try:
        start = get_next_unescaped_appearance(s, lookfor, 0)
        assert s[start:].startswith(lookfor)
    except NotFound:
        return s
    
    before = s[:start]
    consume = consume0= s[start + len(lookfor) - 1:]
    
    opts = []
    args = []
    
#     print('consume= %r'% consume)
    for _ in range(nopt):
        consume = consume_whitespace(consume)
        if not consume or consume[0] != '[':
            print('skipping option')
            opt = None
        else:
            opt_string, consume = get_balanced_brace(consume)
            print('opt string %r consume %r' % (opt_string, consume))
            opt = opt_string[1:-1] # remove brace
        opts.append(opt)
        
    print('after opts= %r'% consume)
    for _ in range(nargs):
        consume = consume_whitespace(consume)
        if not consume or consume[0] != '{':
            msg = 'Command %r: Expected {: got %r. opts=%s args=%s' % (name, consume[0], opts, args)
            character = start 
            character_end =  len(s) - len(consume)
            where = Where(s, character, character_end)
            raise DPSyntaxError(msg, where=where)            
        arg_string, consume2  = get_balanced_brace(consume)
        assert arg_string + consume2 == consume
        consume = consume2
        arg = arg_string[1:-1] # remove brace
        args.append(arg)
    print('substitute_command_ext for %r : args = %s opts = %s consume0 = %r' % (name, args, opts, consume0))
    args = tuple(args)
    opts = tuple(opts)
    replace = f(args=args, opts=opts)
    after_tran = substitute_command_ext(consume, name, f, nargs, nopt)
    res = before + replace + after_tran
    return res

def consume_whitespace(s):
    while s and (s[0] in  [' ']):
        s = s[1:]
    return s

def substitute_command(s, name, sub):
    """
        Subsitute \name{<inside>} with 
        sub : name, inside -> s
    """
    
    start = '\\' + name + '{'
    if not start in s:
        return s
    
    # points to the '{'
    istart = s.index(start)
    i = istart + len(start) -1 # minus brace
    after = s[i:]
#     
#     # don't match '\ciao' when looking for '\c'
#     is_match = not next_char.isalpha()
#     if not is_match:
#         return s[:i] + substitute_command(s[i:], name, sub) 
#     
#     if not after[0] == '{':
#         msg = 'I expected brace after %r, but I see .' % start
#         raise_desc(ValueError, msg, s=s) 
    try:
        assert after[0] == '{'
        inside_plus_brace, after = get_balanced_brace(after)
    except Malformed as e:
        bit = after[:max(len(after), 15 )]
        msg = 'Could not find completion for "%s".' % bit
        raise_wrapped(Malformed, e, msg)
    inside = inside_plus_brace[1:-1]
    replace = sub(name=name, inside=inside)
    before = s[:istart]
    after_tran = substitute_command(after, name, sub)
    res = before + replace + after_tran
    return res
    
    
def get_balanced_brace(s):
    """ s is a string that starts with '{'. 
        returns pair a, b, with a + b = s and 
        a starting and ending with braces
     """
    assert s[0] in ['{', '[']
    stack = []
    i = 0
    while i <= len(s):
        if s[i] == '{':
            stack.append(s[i])
        if s[i] == '[':
            stack.append(s[i])
        if s[i] == '}':
            if not stack or stack[-1] != '{':
                raise Malformed(stack)
            stack.pop()
        if s[i] == ']':
            if not stack or stack[-1] != '[':
                raise Malformed(stack)
            stack.pop()

        if not stack:
            a = s[:i+1]
            b = s[i+1:]
            break
        i += 1
    if stack:
        msg = 'Unmatched braces (stack = %s)' % stack
        raise_desc(Malformed, s, msg)
    assert a[0] in ['{', '['] 
    assert a[-1] in ['}', ']']
    assert a + b == s
    return a, b
    
def replace_quotes(s):
    """ Replaces ``xxx'' sequences """
    START = '``'
    if not START in s:
        return s
    END = "''"
    a = s.index(START)
    if not END in s[a:]:
        return s
    
    b = s.index(END, a) + len(END)
    
    inside = s[a+len(START):b-len(END)]
    if '\n\n' in inside:
        return s
    max_dist = 200
    if len(inside) > max_dist:
        return s
    repl = '&ldquo;' + inside + '&rdquo;'
    s2 = s[:a] + repl + s[b:]
    return replace_quotes(s2)
    
def replace_environment_ext(s, envname, f):
    reg = '\\\\begin{%s}(\\[.*?\\])?(.*?)\\\\end{%s}' % (envname, envname)
    # note multiline and matching '\n'
    reg = re.compile(reg, flags=re.M | re.DOTALL)
    def S(m):
        if m.group(1) is not None:
            opt = m.group(1)[1:-1]
        else:
            opt = None
        inside = m.group(2)
        return f(inside=inside, opt=opt)
    s = re.sub(reg, S, s)
    return s
    
def replace_environment(s, envname, classname, labelprefix):
    def replace_m(inside, opt):
        thm_label = opt
        contents, label = get_s_without_label(inside, labelprefix=labelprefix)
        id_part = "id='%s' "% label if label is not None else ""
        l = "<span class='%s_label latex_env_label'>%s</span>" % (classname, thm_label) if thm_label else ""
        s = '<div %sclass="%s latex_env" markdown="1">%s%s</div>' % (id_part, classname, l, contents)
        return s
    return replace_environment_ext(s, envname, replace_m)
    
def replace_captionsideleft(s):
    assert not 'includegraphics' in s
    def match(matchobj):
        first = matchobj.group(1)
        first2, label = get_s_without_label(first, labelprefix="fig:")
        second = matchobj.group(2)
        if label is not None:
            idpart = ' id="%s"' % label
        else:
            idpart = ""
        res = ('<figure class="captionsideleft"%s>' % idpart)
        res += ('%s<figcaption></figcaption></figure>') % second
        
        print res
        return res
        
    s = re.sub(r'\\captionsideleft{(.*?)}{(.*?)}', 
               match, s, flags=re.M | re.DOTALL)
    return s

def replace_includegraphics(s):
    
#     \includegraphics[scale=0.4]{boot-art/1509-gmcdp/gmcdp_antichains_upsets}
    def match(matchobj):
        latex_options = matchobj.group(1)
        # remove [, ]
        latex_options = latex_options[1:-1]
        latex_path = matchobj.group(2)
        basename = os.path.basename(latex_path)
        res = '<img src="%s.pdf" latex-options="%s" latex-path="%s"/>' % (
                basename, latex_options, latex_path
            )
        return res
        
    s = re.sub(r'\\includegraphics(\[.*?\])?{(.*?)}', 
               match, s, flags=re.M | re.DOTALL)
    return s

def get_s_without_label(contents, labelprefix=None):
    """ Returns a pair s', label 
        where label could be None """
    class Scope:
        def_id = None
    def got_it(m):
        found = m.group(1)
#         print('found : %r' % found)
        if not isinstance(labelprefix, tuple):
            options = (labelprefix,)
        else:
            options = labelprefix
        ok = labelprefix is None or any(_.startswith(labelprefix) for _ in options)
        
        if ok:
            Scope.def_id = found
            # extract
#             print('looking for labelprefix %r found label %r in %s' % ( labelprefix, found, contents))
            return ""
#                 print('got it: %s' % Scope.def_id)
        else:
#             print('not using %r' % ( found))
            # keep 
            return "\\label{%s}" % found
#                 print('rejecting id %r for definition' % m.group(1))
        
    contents2 = re.sub(r'\\label{(.*?)}', got_it, contents)
    return contents2, Scope.def_id
    
def replace_equations(s):
    class Tmp:
        count = 0
        format = None
        
    def replace_eq(matchobj):
        contents = matchobj.group(1)        
        contents2, label = get_s_without_label(contents, labelprefix = None)
        print('contents %r - %r label %r' % (contents, contents2, label))
        if label is not None:
            print('found label %r' % label)
            contents2 +='\\label{%s}' % label
            contents2 +='\\tag{%s}' % (Tmp.count + 1)
            Tmp.count += 1
        f = Tmp.format
        s = f(Tmp(), contents2)
        return s
    
    # do this first
    reg = r'\$\$(.*?)\$\$' 
    Tmp.format = lambda self, x : '$$%s$$' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)

    reg = r'\\\[(.*?)\\\]'
    Tmp.format = lambda self, x : '$$%s$$' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)
    
    reg = r'\\begin{equation}(.*?)\\end{equation}'
    Tmp.format = lambda self, x : '\\begin{equation}%s\\end{equation}' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)
    
    reg = r'\\begin{align}(.*?)\\end{align}'
    Tmp.format = lambda self, x : '\\begin{align}%s\\end{align}' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)
    
    reg = r'\\begin{align\*}(.*?)\\end{align\*}'
    Tmp.format = lambda self, x : '\\begin{align*}%s\\end{align*}' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)

    reg = r'\\begin{eqnarray\*}(.*?)\\end{eqnarray\*}'
    Tmp.format = lambda self, x : '\\begin{eqnarray*}%s\\end{eqnarray*}' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)
    
    reg = r'\\begin{eqnarray}(.*?)\\end{eqnarray}'
    Tmp.format = lambda self, x : '\\begin{eqnarray}%s\\end{eqnarray}' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)

    return s


def get_next_unescaped_appearance(s, d1, search_from):
    while True:
        if not d1 in s[search_from:]:
            raise NotFound()
        maybe = s.index(d1, search_from)
        if s[maybe-1] == '\\':
            search_from = maybe + 1
        else:
            return maybe
        
class NotFound(Exception):
    pass

        
def extract_delimited(s, d1, d2, subs):
    try:
        a = get_next_unescaped_appearance(s, d1, 0)
        b0 = get_next_unescaped_appearance(s, d2, a + len(d1))
        b = b0 + len(d2)
        complete = s[a:b]
    except NotFound:
        return s 
    assert complete.startswith(d1)
    assert complete.endswith(d2)
    #inside = s[a+len(d1):b-len(d2)]
    key = 'KEY%0003dD'% len(subs)
    if 'KEY' in complete:
        msg = 'recursive - %s = %r' % (key, complete)
        msg += '\n\n'
        def abit(s):
            def nl(x):
                return x.replace('\n', ' ↵ ')
            L = len(s)
            if L < 80: return nl(s)
            ss = nl(s[:min(L, 50)])
            se = nl(s[L-min(L, 50):])
            return ss + ' ... ' + se
        for k in sorted(subs):
            msg += '%r = %s\n' % (k, abit(subs[k]))
            
        raise ValueError(msg)
    subs[key] = complete
    
    print ('%r = %s' % (key, complete))
    s2 = s[:a] + key + s[b:]
    return extract_delimited(s2, d1, d2, subs)
    
