
import nltk
from nltk.corpus.reader import dependency
from nltk.util import LazyMap

from dep import depgraph
from dep import depset
import treebank


class CoNLL(treebank.AbstractTreebank, dependency.DependencyCorpusReader):

    def __init__(self, root, files):
        dependency.DependencyCorpusReader.__init__(self, nltk.data.find('corpora/conll06/data/'+root), files)

    """def sents(self, fileids=None):
        f = lambda s: map(lambda x: x[0], s)
        return LazyMap(f, self.tagged_sents(fileids))

    def tagged_sents(self, fileids=None):
        f = lambda s: filter(lambda x: not self.is_punctuation_tag(x[1]), s)
        return LazyMap(f, dependency.DependencyCorpusReader.tagged_sents(self, fileids))
    
    def parsed_sents(self, fileids=None):
        def f(t):
            # XXX: use depgraph.DepGraph.remove_leaves()?
            nodelist = t.nodelist
            new_nodelist = [nodelist[0]]
            i = 1
            for node_dict in nodelist[1:]:
                #if node_dict['tag'] in self.valid_tags:
                if not self.is_punctuation_tag(node_dict['tag']):
                    new_nodelist += [node_dict]
                    node_dict['address'] = i
                    i += 1
                else:
                    node_dict['address'] = -1
            for node_dict in new_nodelist:
                if 'head' in node_dict:
                    node_dict['head'] = nodelist[node_dict['head']]['address']
                deps = node_dict['deps']
                node_dict['deps'] = []
                for d in deps:
                    i = nodelist[d]['address']
                    if i != -1:
                        node_dict['deps'] += [i]
            t.nodelist = new_nodelist

            # wrap into depgraph.DepGraph:
            t = depgraph.DepGraph(t)

            # attach depset:
            t.depset = depset.from_depgraph(t)

            return t
        return LazyMap(f, dependency.DependencyCorpusReader.parsed_sents(self, fileids))"""
    
    def parsed_sents(self, fileids=None):
        def f(t):
            # wrap into depgraph.DepGraph:
            t = depgraph.DepGraph(t)
            # attach depset:
            t.depset = depset.from_depgraph(t)
            return t

        return LazyMap(f, dependency.DependencyCorpusReader.parsed_sents(self, fileids))

    def is_punctuation_tag(self, t):
        """Override in subclasses.
        """
        return False


#
# CORPORA FROM CoNLL-X (2006)
# http://ilk.uvt.nl/conll/post_task_data.html
#
# * Danish, Dutch, Portuguese, Swedish: freely available.
# * Slovene: Slovene Dependency Treebank (http://nl.ijs.si/sdt/)
# * Turkish: METU-Sabanci Turkish Treebank (http://fodor.ii.metu.edu.tr/content/treebank)

class Danish(CoNLL):
    root = 'danish/ddt/'
    files = ['train/danish_ddt_train.conll', 'test/danish_ddt_test.conll']
    train_fileids = files[0]
    test_fileids = files[1]

    def __init__(self):
        CoNLL.__init__(self, self.root, self.files)

    def is_punctuation_tag(self, t):
        return t == 'XP'


class Dutch(CoNLL):
    root = 'dutch/alpino/'
    files = ['train/dutch_alpino_train.conll', 'test/dutch_alpino_test.conll']
    train_fileids = files[0]
    test_fileids = files[1]

    def __init__(self):
        CoNLL.__init__(self, self.root, self.files)

    def is_punctuation_tag(self, t):
        # n['tag'] is the fifth column.
        return t == 'Punc'


class Portuguese(CoNLL):
    root = 'portuguese/bosque/'
    files = ['treebank/portuguese_bosque_train.conll', 'test/portuguese_bosque_test.conll']
    train_fileids = files[0]
    test_fileids = files[1]

    def __init__(self):
        CoNLL.__init__(self, self.root, self.files)

    def is_punctuation_tag(self, t):
        return t == 'punc'


class Swedish(CoNLL):
    root = 'swedish/talbanken05/'
    files = ['train/swedish_talbanken05_train.conll', 'test/swedish_talbanken05_test.conll']
    train_fileids = files[0]
    test_fileids = files[1]

    def __init__(self):
        CoNLL.__init__(self, self.root, self.files)

    def is_punctuation_tag(self, t):
        return t.startswith('I')


class Slovene(CoNLL):
    root = 'slovene/sdt/'
    files = ['treebank/slovene_sdt_train.conll', 'test/slovene_sdt_test.conll']
    train_fileids = files[0]
    test_fileids = files[1]

    def __init__(self):
        CoNLL.__init__(self, self.root, self.files)

    def is_punctuation_tag(self, t):
        return t == 'PUNC'


class Turkish(CoNLL):
    root = 'turkish/metu_sabanci/'
    files = ['train/turkish_metu_sabanci_train.conll', \
                'test/turkish_metu_sabanci_test.conll']

    train_fileids = files[0]
    test_fileids = files[1]

    def __init__(self):
        CoNLL.__init__(self, self.root, self.files)

    def is_punctuation_tag(self, t):
        return t == 'Punc'
