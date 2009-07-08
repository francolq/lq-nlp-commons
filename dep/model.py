from __future__ import absolute_import
# dep/model.py: A general model for dependency parsing (class DepModel).

import itertools

#from .. import model
import model
import sentence
from dep import depset
from dep import dwsj

class DepModel(model.Model):
    count_length_2 = True
    count_length_2_1 = False
    
    
    def __init__(self, treebank=None):
        
        treebank = self._get_treebank(treebank)
        
        S, Gold = [], []
        for t in treebank.get_trees():
            s = sentence.Sentence(t.leaves())
            S += [s]
            Gold += [depset.deptree_to_depset(t)]
        
        self.S = S
        self.Gold = Gold
    
    
    def _get_treebank(self, treebank=None):
        if treebank is None:
            treebank = dwsj.DepWSJ10()
        return treebank
    
    
    def eval(self, output=True, short=False, long=False, max_length=10):
        Gold = self.Gold
        
        Count = 0
        Directed = 0.0
        Undirected = 0.0
        
        for i in range(len(Gold)):
            l = Gold[i].length
            if l <= max_length and (self.count_length_2_1 or (self.count_length_2 and l == 2) or l >= 3):
                (count, directed, undirected) = self.measures(i)
                Count += count
                Directed += directed
                Undirected += undirected
        
        Directed = Directed / Count
        Undirected = Undirected / Count
        
        self.evaluation = (Count, Directed, Undirected)
        self.evaluated = True
        
        if output and not short:
            print "Number of Trees:", len(Gold)
            print "  Directed Accuracy: %2.1f" % (100*Directed)
            print "  Undirected Accuracy: %2.1f" % (100*Undirected)
        elif output and short:
            print "L =", Directed, "UL =", Undirected
        
        return self.evaluation
    
    
    def measures(self, i):
        # Helper for eval().
        # Measures for the i-th parse.
        
        g, p = self.Gold[i].deps, self.Parse[i].deps
        (n, d, u) = (self.Gold[i].length, 0, 0)
        for (a, b) in g:
            b1 = (a, b) in p
            b2 = (b, a) in p
            if b1:
                d += 1
            if b1 or b2:
                u += 1
        
        return (n, d, u)
