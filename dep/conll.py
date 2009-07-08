# conll.py: Classes to read CoNLL 2006 and 2007 corpora.
# TODO: test projectiveness and project the dependency trees.
#
#__author__="francolq"
#__date__ ="$29-jun-2009 1:13:49$"

from nltk.corpus.reader import dependency
from nltk import tree
from nltk import corpus
from nltk.util import LazyMap

from dep import depgraph
import treebank

class CoNLLTreebank(treebank.Treebank):
    def __init__(self, corpus, files=None, max_length=None):
        treebank.Treebank.__init__(self)
        self.corpus = corpus
        self.trees = []
        #print is_punctuation
        i = 0
        non_projectable, empty = 0, 0
        for d in self.corpus.parsed_sents(files):
            d2 = depgraph.DepGraph(d)
            try:
                t = d2.constree()
            except:
                #t2 = None
                non_projectable += 1
            else:
                t2 = CoNLLTree(t)
                t2.remove_leaves()
                t2.remove_punctuation(type(self).is_punctuation)
                s = t2.leaves()
                if s != [] and (max_length is None or len(s) <= max_length):
                    t2.corpus_index = i
                    self.trees += [t2]
                else:
                    empty += 1
            i += 1
        self.non_projectable = non_projectable
        self.empty = empty
    
    @staticmethod
    def is_punctuation(s):
        return False

    # FIXME: overriden because words are removed and tags are leaves.
    # don't remove words.
    def tagged_sents(self):
        # LaxyMap from nltk.util:
        f = lambda t: [(x,x) for x in t.leaves()]
        return LazyMap(f,  self.get_trees())


class CoNLL06Treebank(CoNLLTreebank):
    def __init__(self, root, files, max_length=None):
        corpus = dependency.DependencyCorpusReader(root, files)
        CoNLLTreebank.__init__(self, corpus, None, max_length)


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
    root = '/Users/francolq/Documents/comp/doctorado/corpus/conll06/data/turkish/metu_sabanci/'
    files = ['train/turkish_metu_sabanci_train.conll', \
                'test/turkish_metu_sabanci_test.conll']
    
    def __init__(self, max_length=None):
        CoNLL06Treebank.__init__(self, self.root, self.files, max_length)

    @staticmethod
    def is_punctuation(s):
        return s == 'Punc'


class Danish(CoNLL06Treebank):
    root = '/Users/francolq/Documents/comp/doctorado/corpus/conll06/data/danish/ddt/'
    files = ['train/danish_ddt_train.conll', 'test/danish_ddt_test.conll']

    def __init__(self, max_length=None):
        CoNLL06Treebank.__init__(self, self.root, self.files, max_length)

    @staticmethod
    def is_punctuation(s):
        return s == 'XP'


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
