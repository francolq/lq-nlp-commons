# depset.py: Dependency set.
#


class DepSet:
    
    def __init__(self, length, deps):
        self.length = length
        self.deps = deps


def from_depgraph(g):
    length = len(g.nodelist)-1
    deps = [(n['address']-1, n['head']-1) for n in g.nodelist[1:]]
    return DepSet(length, deps)


def from_string(s):
    """
    >>> d = from_string('[(0,3), (1,0), (2,1), (3,-1)]\n')
    """
    t = s[1:].split()
    l = len(t)
    deps = []
    for x in t:
        y = x[1:-2].split(',')
        deps += [(int(y[0]), int(y[1]))]
    return DepSet(l, deps)


def deptree_to_depset(t):
    return DepSet(len(t.leaves()), t.depset)


def lhead_depset(length):
    deps = [(i, i-1) for i in range(length)]
    return DepSet(length, deps)


def rhead_depset(length):
    deps = [(i, i+1) for i in range(length-1)] + [(length-1, -1)]
    return DepSet(length, deps)
