from __future__ import absolute_import
# dep/model.py: A general model for dependency parsing (class DepModel), and a
# general model for projective dependency parsing, with evaluation also as
# constituent trees.


#from .. import model
import sentence
import bracketing
import model
from dep import depset
from dep import dwsj


class DepModel(model.Model):
    """A general model for dependency parsing."""
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
    
    
    def eval(self, output=True, short=False, long=False, max_length=None):
        Gold = self.Gold
        
        Count = 0
        Directed = 0.0
        Undirected = 0.0
        
        for i in range(len(Gold)):
            l = Gold[i].length
            if (max_length is None or l <= max_length) \
                    and (self.count_length_2_1 or (self.count_length_2 and l == 2) or l >= 3):
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


class ProjDepModel(DepModel):
    """A general model for projective dependency parsing, with evaluation also
    as constituent trees.
    """
    def __init__(self, treebank=None, training_corpus=None):
        """
        The elements of the treebank must be trees with a DepSet in the
        attribute depset.
        """
        treebank = self._get_treebank(treebank)
        if training_corpus == None:
            training_corpus = treebank
        self.test_corpus = treebank
        self.training_corpus = training_corpus
        S = []
        for s in treebank.tagged_sents():
            s = [x[1] for x in s]
            S += [sentence.Sentence(s)]
        self.S = S
        # Extract gold as DepSets:
        # FIXME: call super and do this there.
        self.Gold = [t.depset for t in treebank.parsed_sents()]
        
        # Exctract gold as Bracketings:
        self.bracketing_model = model.BracketingModel(treebank)
    
    def eval(self, output=True, short=False, long=False, max_length=None):
        """Compute evaluation of the parses against the test corpus. Computes
        unlabeled precision, recall and F1 between the bracketings, and directed
        and undirected dependency accuracy between the dependency structures.
        """
        # XXX: empezamos a lo bruto:
        self.bracketing_model.Parse = [bracketing.tree_to_bracketing(t) for t in self.Parse]
        #dmvccm.DMVCCM.eval(self, output, short, long, max_length)
        self.bracketing_model.eval(output, short, long, max_length)

        # Ahora eval de dependencias:
        self.DepParse = self.Parse
        self.Parse = [type(self).tree_to_depset(t) for t in self.DepParse]
        #model.DepModel.eval(self, output, short, long, max_length)
        DepModel.eval(self, output, short, long, max_length)
        self.Parse = self.DepParse

    @staticmethod
    def tree_to_depset(t):
        """Function used to convert the trees returned by the parser to DepSets.
        """
        raise Exception('Static function tree_to_depset must be overriden.')
