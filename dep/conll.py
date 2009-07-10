# conll.py: Classes to read CoNLL 2006 and 2007 corpora.
# TODO: test projectiveness and project the dependency trees.
#
#__author__="francolq"
#__date__ ="$29-jun-2009 1:13:49$"

from nltk.corpus.reader import dependency
from nltk import tree
from nltk import corpus

from dep import depgraph
from dep import depset
import treebank

class CoNLLTreebank(treebank.Treebank):
    def __init__(self, corpus, files=None, max_length=None):
        treebank.Treebank.__init__(self)
        self.corpus = corpus
        self.trees = []
        #print is_punctuation
        i = 0
        non_projectable, empty = 0, 0
        non_leaf = []
        for d in self.corpus.parsed_sents(files):
            d2 = depgraph.DepGraph(d)
            try:
                d2.remove_leaves(type(self).is_punctuation)
                t = d2.constree()
            except Exception as e:
                msg = e[0]
                if msg.startswith('Non-projectable'):
                    non_projectable += 1
                else:
                    non_leaf += [i]
            else:
                s = t.leaves()
                if s != [] and (max_length is None or len(s) <= max_length):
                    t.corpus_index = i
                    t.depset = depset.from_depgraph(d2)
                    self.trees += [t]
                else:
                    empty += 1
            i += 1
        self.non_projectable = non_projectable
        self.empty = empty
        self.non_leaf = non_leaf
    
    @staticmethod
    def is_punctuation(n):
        return False


class CoNLL06Treebank(CoNLLTreebank):
    def __init__(self, root, files, max_length=None):
        corpus = dependency.DependencyCorpusReader(root, files)
        CoNLLTreebank.__init__(self, corpus, None, max_length)


class Turkish(CoNLL06Treebank):
    root = '/Users/francolq/Documents/comp/doctorado/corpus/conll06/data/turkish/metu_sabanci/'
    files = ['train/turkish_metu_sabanci_train.conll', \
                'test/turkish_metu_sabanci_test.conll']
    
    def __init__(self, max_length=None):
        CoNLL06Treebank.__init__(self, self.root, self.files, max_length)

    @staticmethod
    def is_punctuation(n):
        return n['tag'] == 'Punc'


class Danish(CoNLL06Treebank):
    root = '/Users/francolq/Documents/comp/doctorado/corpus/conll06/data/danish/ddt/'
    files = ['train/danish_ddt_train.conll', 'test/danish_ddt_test.conll']

    def __init__(self, max_length=None):
        CoNLL06Treebank.__init__(self, self.root, self.files, max_length)

    @staticmethod
    def is_punctuation(n):
        return n['tag'] == 'XP'


class Catalan(CoNLLTreebank):
    def __init__(self):
        CoNLLTreebank.__init__(self, corpus.conll2007, ['cat.test', 'cat.train'])

    @staticmethod
    def is_punctuation(n):
        return n['tag'].lower()[0] == 'f'


class Basque(CoNLLTreebank):
    def __init__(self):
        CoNLLTreebank.__init__(self, corpus.conll2007, ['eus.test', 'eus.train'])

    @staticmethod
    def is_punctuation(n):
        return n['tag'] == 'PUNT'
