
import sys
u = unicode(sys.stdin.read(), 'utf-8')

u2 = u''
s = set()
for c in u:
    i = ord(c)
    if i > 128:
        u2 += c
        s.add(c)

x = "".join(sorted(list(s)))

print(x)