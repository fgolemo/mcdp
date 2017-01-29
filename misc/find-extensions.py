# find src/mcdp_data |  python misc/find-extensions.py
import sys, os
data = sys.stdin.read()
exts = set()
from collections import Counter
c = Counter()
for fn in data.split('\n'):
    ext = os.path.splitext(fn)[1]
    c[ext] += 1

pairs = sorted(c.items(), key=lambda _:- _[1])
print("\n".join('%25s %d' % p for p in pairs))
