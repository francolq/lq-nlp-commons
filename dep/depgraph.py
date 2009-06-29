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
            return tree.Tree(node['tag'], [word])
        address = node['address']
        ldeps = [i for i in deps if i < address]
        rdeps = [i for i in deps if i > address]
        lsubtrees = [self._constree(i) for i in ldeps]
        rsubtrees = [self._constree(i) for i in rdeps]
        csubtree = tree.Tree(node['tag'], [word])
        
        return tree.Tree(word, lsubtrees+[csubtree]+rsubtrees)
