# Copyright (C) 2007-2011 Franco M. Luque
# URL: <http://www.cs.famaf.unc.edu.ar/~francolq/>
# For license information, see LICENSE.txt

# depset.py: Dependency set.


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
    deps = eval(s)
    return DepSet(len(deps), deps)


def deptree_to_depset(t):
    return DepSet(len(t.leaves()), t.depset)


def lhead_depset(length):
    deps = [(i, i-1) for i in range(length)]
    return DepSet(length, deps)


def rhead_depset(length):
    deps = [(i, i+1) for i in range(length-1)] + [(length-1, -1)]
    return DepSet(length, deps)


def binary_depsets(n):
    """Returns all the binary dependency trees for a sentence of length n.
    """
    return map(lambda s: DepSet(n, s), _binary_depsets(n))


def _binary_depsets(n):
    """Helper for binary_depsets.
    """
    if n == 0:
        return [[]]
    elif n == 1:
        return [[(0, -1)]]
    else:
        result = []
        for i in range(n):
            lres = _binary_depsets(i)
            rres = _binary_depsets(n-1-i)
            lres = map(lambda l: [(j, (k!=-1 and k) or i) for (j,k) in l], lres)
            rres = map(lambda l: [(j+i+1, (k!=-1 and (k+i+1)) or i) for (j,k) in l], rres)
            #print i, lres, rres
            result += [l+[(i, -1)]+r for l in lres for r in rres]

        return result


def all_depsets(n):
    chart = {}
    for i in range(n):
        chart[i, i+1, 'lc'] = [[]]
        chart[i, i+1, 'rc'] = [[]]

    for width in range(2, n+1):
        for i in range(n-width+1):
            k = i + width

            # combination B (produces incomplete spans)
            chart[i, k, 'li'] = []
            chart[i, k, 'ri'] = []
            for j in range(i+1, k):
                c1 = chart[i, j, 'lc']
                c2 = chart[j, k, 'rc']
                c3 = [x+y for x in c1 for y in c2]
                # produce a li
                chart[i, k, 'li'] += map(lambda z: z+[(k-1, i)], c3)
                # produce a ri
                chart[i, k, 'ri'] += map(lambda z: [(i, k-1)]+z, c3)

            # combination A (produces complete spans)
            chart[i, k, 'lc'] = []
            for j in range(i+2, k+1):
                # consider combination of (i,j) with (j,k):
                c1 = chart[i, j, 'li']
                c2 = chart[j-1, k, 'lc']
                chart[i, k, 'lc'] += [x+y for x in c1 for y in c2]
            chart[i, k, 'rc'] = []
            for j in range(i, k-1):
                # consider combination of (i,j) with (j,k):
                c1 = chart[i, j+1, 'rc']
                c2 = chart[j, k, 'ri']
                chart[i, k, 'rc'] += [x+y for x in c1 for y in c2]

    # ad-hoc code for the root:
    chart[n, n+1, 'rc'] = [[]]
    k = n+1
    for i in range(n-1, -1, -1):
            # combination B (produces incomplete spans)
            j = k-1
            c1 = chart[i, j, 'lc']
            c2 = chart[j, k, 'rc']
            c3 = [x+y for x in c1 for y in c2]
            chart[i, k, 'ri'] = map(lambda z: [(i, -1)]+z, c3)

            # combination A (produces complete spans)
            chart[i, k, 'rc'] = []
            for j in range(i, k-1):
                c1 = chart[i, j+1, 'rc']
                c2 = chart[j, k, 'ri']
                chart[i, k, 'rc'] += [x+y for x in c1 for y in c2]

    return chart[0, n+1, 'rc']
