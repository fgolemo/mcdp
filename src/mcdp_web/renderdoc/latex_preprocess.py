import re

def replace_environment(s, envname, classname, labelprefix):
    def replace_def(matchobj):
        if matchobj.group(1) is None:
            label =  None
        else:
            label =  matchobj.group(1)[1:-1] # remove [ ] 
        contents = matchobj.group(2)
        
        class Scope:
            def_id = None
        def got_it(m):
            found = m.group(1)
            ok = labelprefix is not None or labelprefix in found
            if ok:
                Scope.def_id = m.group(1)
                # extract
                print('using for env %s in %s' % (envname, found))
                return ""
#                 print('got it: %s' % Scope.def_id)
            else:
                print('keeping %s in %s' % (envname, found))
                # keep 
                return "\\label{%s}" % found
                pass
#                 print('rejecting id %r for definition' % m.group(1))
            
        contents = re.sub(r'\\label{(.*?)}', got_it, contents)
#         print 'replace_def(%s, %s)' % (label, Scope.def_id)
        id_part = "id='%s' "% Scope.def_id if Scope.def_id is not None else ""
        l = "<span class='%s_label latex_env_label'>%s</span>" % (classname, label) if label else ""
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
    
def latex_preprocessing(s):
    s = s.replace('~$', '&nbsp;$')
    # note: nongreedy matching ("?" after *);
    
    
    s = re.sub(r'\\cite\[(.*)?\]{(.*?)}', r'<cite id="\2">[\1]</cite>', s)
    s = re.sub(r'\\cite{(.*?)}', r'<cite id="\1" replace="true">[\1]</cite>', s)
    
    # note: nongreedy matching ("?" after *); and multiline (re.M) DOTALL = '\n' part of .
    s = re.sub(r'\\emph{(.*?)}', r'<em>\1</em>', s, flags=re.M | re.DOTALL)
    s = re.sub(r'\\textbf{(.*?)}', r'<strong>\1</strong>', s, flags=re.M | re.DOTALL)
    s = s.replace('~"', '&nbsp;&ldquo;')
    s = s.replace('%\n', '\n')
    s = replace_equations(s) 
    s = replace_environment(s, "defn", "definition", "def:")
    s = replace_environment(s, "lem", "lemma", "lem:")
    s = replace_environment(s, "rem", "remark", "rem:")
    s = replace_environment(s, "example", "example", "exa:")
    
    s = s.replace('\\scottcontinuity', 'Scott continuity')
    s = s.replace('\\scottcontinuous', 'Scott continuous')
    
    if 'defn' in s:
        raise ValueError(s)
     
    return s
    
    
def replace_equations(s):
    def replace_eq(matchobj):
        contents = matchobj.group(1)
        
        labelprefix = "eq:"
        class Scope:
            def_id = None
        def got_it(m):
            found = m.group(1)
            ok = labelprefix is not None or labelprefix in found
            if ok:
                Scope.def_id = found
                # extract
                print('using for equation %s' % ( found))
                return ""
#                 print('got it: %s' % Scope.def_id)
            else:
                print('keeping equation in %s' % ( found))
                # keep 
                return "\\label{%s}" % found
                pass
#                 print('rejecting id %r for definition' % m.group(1))
            
        contents = re.sub(r'\\label{(.*?)}', got_it, contents)
#         print 'replace_def(%s, %s)' % (label, Scope.def_id)
#         id_part = "id='%s' "% Scope.def_id if Scope.def_id is not None else ""
#         l = "<span class='%s_label latex_env_label'>%s</span>" % (classname, label) if label else ""
        s = '\n\n$$%s$$\n\n' % contents
        return s
    reg = r'\\\[(.*?)\\\]'
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)
    reg = r'\\begin{equation}(.*?)\\end{equation}'
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)

    return s