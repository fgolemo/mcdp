import re
import os


def latex_preprocessing(s):
    s = s.replace('~$', '&nbsp;$')
    # note: nongreedy matching ("?" after *);
    def fix(m):
        x=m.group(1)
        if not 'eq:' in x:
            print('fixing %r to eq:%s' % (x, x))
            x = 'eq:' + x
        return '\\eqref{%s}' %x
    s = re.sub(r'\\eqref{(.*?)}', fix, s)
    
    s = re.sub(r'\\cite\[(.*)?\]{(.*?)}', r'<cite id="\2">[\1]</cite>', s)
    s = re.sub(r'\\cite{(.*?)}', r'<cite id="\1" replace="true">[\1]</cite>', s)
    
    # note: nongreedy matching ("?" after *); and multiline (re.M) DOTALL = '\n' part of .
    s = re.sub(r'\\emph{(.*?)}', r'<em>\1</em>', s, flags=re.M | re.DOTALL)
    s = re.sub(r'\\textbf{(.*?)}', r'<strong>\1</strong>', s, flags=re.M | re.DOTALL)
    s = s.replace('~"', '&nbsp;&ldquo;')
    s = s.replace('%\n', '\n')
    s = replace_equations(s) 
    s = replace_includegraphics(s)
    s = replace_captionsideleft(s)
    s = replace_environment(s, "defn", "definition", "def:")
    s = replace_environment(s, "lem", "lemma", "lem:")
    s = replace_environment(s, "rem", "remark", "rem:")
    s = replace_environment(s, "example", "example", "exa:")
    
    s = s.replace('\\scottcontinuity', 'Scott continuity')
    s = s.replace('\\scottcontinuous', 'Scott continuous')
    
    if 'defn' in s:
        raise ValueError(s)
     
    return s
    
    
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
        s = '<div %sclass="%s latex_env">%s%s</div>' % (id_part, classname, l, contents)
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
        second = matchobj.group(2)
        res = ('<figure class="captionsideleft">'
               +'%s<figcaption>Standard figure caption</figcaption></figure>') % second
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
            print('looking for labelprefix %r found label %r in %s' % ( labelprefix, found, contents))
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

