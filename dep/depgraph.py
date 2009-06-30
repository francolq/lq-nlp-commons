__author__="francolq"
__date__ ="$28-jun-2009 20:11:04$"

from nltk.parse import dependencygraph
from nltk import tree

import treebank

class DepGraph(dependencygraph.DependencyGraph):

    def __init__(self, nltk_depgraph):
        dependencygraph.DependencyGraph.__init__(self)
        self.nodelist = nltk_depgraph.nodelist
        self.root = nltk_depgraph.root
        self.stream = nltk_depgraph.stream
    
    def constree(self):
        i = self.root['address']
        return treebank.Tree(self._constree(i))
    
    def _constree(self, i):
        node = self.nodelist[i]
        word = node['word']
        deps = node['deps']
        if len(deps) == 0:
            t = tree.Tree(node['tag'], [word])
            t.span = (i, i+1)
            return t
        address = node['address']
        ldeps = [j for j in deps if j < address]
        rdeps = [j for j in deps if j > address]
        lsubtrees = [self._constree(j) for j in ldeps]
        rsubtrees = [self._constree(j) for j in rdeps]
        csubtree = tree.Tree(node['tag'], [word])
        csubtree.span = (i, i+1)
        subtrees = lsubtrees+[csubtree]+rsubtrees
        
        # check projectivity:
        for j in range(len(subtrees)-1):
            if subtrees[j].span[1] != subtrees[j+1].span[0]:
                raise Exception('Non-projectable dependency graph.')
        
        t = tree.Tree(word, subtrees)
        j = subtrees[0].span[0]
        k = subtrees[-1].span[1]
        t.span = (j, k)
        return t
