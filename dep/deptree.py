# deptree.py: Dependency tree.
#
# FIXME: confusing class names DepTree and deptreebank,DepTree.

class DepTree:
    
    
    def __init__(self, length, deps):
        self.length = length
        self.deps = deps


def tree_to_deptree(t):
    l = len(t.leaves())
    return DepTree(l, t.depset)


def lhead_deptree(length):
    depset = set((i, i-1) for i in range(length))
    return DepTree(length, depset)


def rhead_deptree(length):
    depset = set((i, i+1) for i in range(length-1))
    depset.add((length-1, -1))
    return DepTree(length, depset)
