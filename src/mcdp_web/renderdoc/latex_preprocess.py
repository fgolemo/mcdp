import re
import os
from contracts.utils import raise_desc


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
    
#     s = re.sub(r'\\textendash\\s*', '&ndash;', s) # XXX
    
    s = re.sub(r'\\noindent\s*', '', s) # XXX
# {[}m{]}}, and we need to choose the \R{endurance~$T$~{[}s{]}}
    s = re.sub(r'{(\[|\])}', r'\1', s)
#     s = re.sub(r'\\R{(.*?)}', r'<r>\1</r>', s)
#     s = re.sub(r'\\F{(.*?)}', r'<f>\1</f>', s)
#     
    s = re.sub(r'\\ref{(.*?)}', r'<a href="#\1"></a>', s)
    
    # \vref
    s = re.sub(r'\\vref{(.*?)}', r'<a class="only-number" href="#\1"></a>', s)
       
    s = re.sub(r'\\eqref{(.*?)}', r'<a href="#eq:\1"></a>', s)
    s = re.sub(r'\\tabref{(.*?)}', r'<a href="#tab:\1"></a>', s)
    s = re.sub(r'\\figref{(.*?)}', r'<a href="#fig:\1"></a>', s)
    s = re.sub(r'\\proref{(.*?)}', r'<a href="#prop:\1"></a>', s)
    s = re.sub(r'\\propref{(.*?)}', r'<a href="#prop:\1"></a>', s)
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
    
    s = s.replace('\etal', 'et. al.')
    s = replace_equations(s) 
    s = replace_includegraphics(s)
    s = replace_captionsideleft(s)
    s = replace_environment(s, "defn", "definition", "def:")
    s = replace_environment(s, "lem", "lemma", "lem:")
    s = replace_environment(s, "rem", "remark", "rem:")
    s = replace_environment(s, "thm", "thorem", "thm:")
    s = replace_environment(s, "prop", "proposition", "prop:")
    s = replace_environment(s, "example", "example", "exa:")
    s = replace_environment(s, "proof", "proof", "proof:")
    s = replace_environment(s, "problem", "problem", "prob:")
    s = replace_environment(s, "figure", "figure", "fig:")
    
    s = replace_environment(s, "centering", "centering", None)
    
    s = substitute_command(s, 'fbox', lambda name, inside: 
                           '<div class="fbox">' + inside + "</div>" )
    s = substitute_command(s, 'caption', lambda name, inside: 
                           '<figcaption>' + inside + "</figcaption>" )
    s = s.replace('\\scottcontinuity', 'Scott continuity')
    s = s.replace('\\scottcontinuous', 'Scott continuous')
    
    s = replace_quotes(s)
#     if 'defn' in s:
#         raise ValueError(s)
     
    return s
  

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
  
def substitute_command(s, name, sub):
    """
        Subsitute \name{<inside>} with 
        sub : name, inside -> s
    """
    
    start = '\\' + name
    if not start in s:
        return s
    
    # points to the '{'
    istart = s.index(start)
    i = istart + len(start)
    after = s[i:]
    if not after[0] == '{':
        msg = 'I expected brace after %r.' % start
        raise_desc(ValueError, msg, s=s) 
    inside_plus_brace, after = get_balanced_brace(after)
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
    assert s[0] == '{'
    n = 0 # number of levels
    i = 0
    while i <= len(s):
        if s[i] == '{':
            n += 1
        if s[i] == '}':
            n -= 1
            if n == 0:
                a = s[:i+1]
                b = s[i+1:]
                break
        i += 1
    if n > 0:
        msg = 'Unmatched braces (level = %d)' % n
        raise_desc(ValueError, s, msg)
    assert a[0] == '{'
    assert a[-1] == '}'
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
    
def replace_environment(s, envname, classname, labelprefix):
    def replace_def(matchobj):
        if matchobj.group(1) is None:
            thm_label =  None
        else:
            thm_label =  matchobj.group(1)[1:-1] # remove [ ] 
        contents = matchobj.group(2)
        
        contents, label = get_s_without_label(contents, labelprefix=labelprefix)
#         print 'replace_def(%s, %s)' % (label, Scope.def_id)
        id_part = "id='%s' "% label if label is not None else ""
        l = "<span class='%s_label latex_env_label'>%s</span>" % (classname, thm_label) if thm_label else ""
        s = '<div %sclass="%s latex_env" markdown="1">%s%s</div>' % (id_part, classname, l, contents)
        return s
    
    reg = '\\\\begin{%s}(\\[.*?\\])?(.*?)\\\\end{%s}' % (envname, envname)
    # note multiline and matching '\n'
    reg = re.compile(reg, flags=re.M | re.DOTALL)
    
 
    t=u"""\\begin{defn}[Width and height of a poset]
\\label{def:poset-width-height} $\mathsf{width}(\posA)$ is the maximum
cardinality of an antichain in~$\posA$ and $\mathsf{height}(\posA)$
is the maximum cardinality of a chain in~$\posA$.
\\end{defn}
"""
    if envname == 'defn':
        tmatch= reg.match(t)
        if tmatch is None:
            raise ValueError(t)
    s = re.sub(reg, replace_def, s)
    return s
    
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
    """ Returns a pair s', prefix 
        where label could be None """
    class Scope:
        def_id = None
    def got_it(m):
        found = m.group(1)
#         print('found : %r' % found)
        ok = labelprefix is None or labelprefix in found
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
    Tmp.format = lambda self, x : '$$%s$$' % x
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

