# depset.py: Dependency set.
#


class DepSet:
    
    def __init__(self, length, deps):
        self.length = length
        self.deps = deps


def deptree_to_depset(t):
    l = len(t.leaves())
    return DepSet(l, t.depset)


def lhead_depset(length):
    deps = [(i, i-1) for i in range(length)]
    return DepSet(length, deps)


def rhead_depset(length):
    deps = [(i, i+1) for i in range(length-1)] + [(length-1, -1)]
    return DepSet(length, deps)
