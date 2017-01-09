#!/usr/bin/env python2
import sys

s = sys.stdin.read()

B = r'\begin{document}'
E = r'\end{document}'


s = s.replace('<=','&lt;=')
s = s.replace('>=','&gt;=')
s = s.replace('\t', ' '*4)
s = s[s.index(B)+len(B):]
s = s[:s.index(E)]

s = s.replace('~', ' ')

sys.stdout.write(s)
