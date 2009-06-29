# conll.py: Classes to read CoNLL 2006 and 2007 corpora.
# TODO: test projectiveness and project the dependency trees.
#
#__author__="francolq"
#__date__ ="$29-jun-2009 1:13:49$"

from nltk.corpus.reader import dependency
from nltk import tree
from nltk import corpus

from dep import depgraph
import treebank

class CoNLLTreebank(treebank.Treebank):
    def __init__(self, corpus, files=None):
        treebank.Treebank.__init__(self)
        self.corpus = corpus
        self.trees = []
        #print is_punctuation
        for d in self.corpus.parsed_sents(files):
            d2 = depgraph.DepGraph(d)
            t = d2.constree()
            t2 = CoNLLTree(t)
            t2.remove_leaves()
            t2.remove_punctuation(type(self).is_punctuation)
            self.trees += [t2]
    
    @staticmethod
    def is_punctuation(s):
        return False


class CoNLL06Treebank(CoNLLTreebank):
    def __init__(self, root, files):
        corpus = dependency.DependencyCorpusReader(root, files)
        CoNLLTreebank.__init__(self, corpus)


class CoNLLTree(treebank.Tree):
    def remove_punctuation(self, is_punctuation):
        def f(t):
            if isinstance(t, tree.Tree):
                punctuation = True
                for leave in t.leaves():
                    punctuation = punctuation and is_punctuation(leave)
                return not punctuation
            else:
                return not is_punctuation(t)
        self.filter_subtrees(f)


class Turkish(CoNLL06Treebank):
    root = '/Users/francolq/Documents/comp/doctorado/corpus/Turco/data/turkish/metu_sabanci/train'
    files = ['turkish_metu_sabanci_train.conll']
    
    def __init__(self):
        CoNLL06Treebank.__init__(self, self.root, self.files)

    @staticmethod
    def is_punctuation(s):
        return s == 'Punc'


class Catalan(CoNLLTreebank):
    def __init__(self):
        CoNLLTreebank.__init__(self, corpus.conll2007, ['cat.test', 'cat.train'])

    @staticmethod
    def is_punctuation(s):
        return s.lower()[0] == 'f'


class Basque(CoNLLTreebank):
    def __init__(self):
        CoNLLTreebank.__init__(self, corpus.conll2007, ['eus.test', 'eus.train'])

    @staticmethod
    def is_punctuation(s):
        return s == 'PUNT'
