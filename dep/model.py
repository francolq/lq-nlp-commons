from __future__ import absolute_import
# dep/model.py: A general model for dependency parsing (class DepModel).

import itertools

#from .. import model
import model
import sentence
from . import deptree

class DepModel(model.Model):
    count_length_2 = True
    count_length_2_1 = False
    
    
    def __init__(self, treebank=None):
        
        treebank = self._get_treebank(treebank)
        
        S, Gold = [], []
        for t in treebank.get_trees():
            s = sentence.Sentence(t.leaves())
            S += [s]
            Gold += [deptree.tree_to_deptree(t)]
        
        self.S = S
        self.Gold = Gold
    
    
    def _get_treebank(self, treebank=None):
        if treebank is None:
            import dep.dwsj
            treebank = dwsj.DepWSJ10()
        return treebank
    
    
    def eval(self, output=True, short=False, long=False, max_length=10):
        Gold = self.Gold
        
        Count = 0
        Labeled = 0.0
        Unlabeled = 0.0
        
        for i in range(len(Gold)):
            l = Gold[i].length
            if l <= max_length and (self.count_length_2_1 or (self.count_length_2 and l == 2) or l >= 3):
                (count, labeled, unlabeled) = self.measures(i)
                Count += count
                Labeled += labeled
                Unlabeled += unlabeled
        
        Labeled = Labeled / Count
        Unlabeled = Unlabeled / Count
        
        self.evaluation = (Count, Labeled, Unlabeled)
        self.evaluated = True
        
        if output and not short:
            print "Number of Trees:", len(Gold)
            print "  Labeled Accuracy: %2.1f" % (100*Labeled)
            print "  Unlabeled Accuracy: %2.1f" % (100*Unlabeled)
        elif output and short:
            print "L =", Labeled, "UL =", Unlabeled
        
        return self.evaluation
    
    
    def measures(self, i):
        # Helper for eval().
        # Measures for the i-th parse.
        
        g, p = self.Gold[i].deps, self.Parse[i].deps
        (n, l, u) = (self.Gold[i].length, 0, 0)
        for (a, b) in g:
            b1 = (a, b) in p
            b2 = (b, a) in p
            if b1:
                l += 1
            if b1 or b2:
                u += 1
        
        return (n, l, u)
