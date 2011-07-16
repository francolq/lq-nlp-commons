
import nltk
from nltk.corpus.reader import dependency
from nltk.util import LazyMap

from dep import depgraph
from dep import depset
import treebank


class CoNLL(treebank.AbstractTreebank, dependency.DependencyCorpusReader):

    def __init__(self, root, files):
        dependency.DependencyCorpusReader.__init__(self, nltk.data.find('corpora/conll06/data/'+root), files)

    def sents(self, fileids=None):
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
        return LazyMap(f, dependency.DependencyCorpusReader.parsed_sents(self, fileids))

    def is_punctuation_tag(self, t):
        """Override in subclasses.
        """
        return False


class Danish(CoNLL):
    root = 'danish/ddt/'
    files = ['train/danish_ddt_train.conll', 'test/danish_ddt_test.conll']
    train_fileids = files[0]
    test_fileids = files[1]

    def __init__(self):
        CoNLL.__init__(self, self.root, self.files)

    def is_punctuation_tag(self, t):
        return t == 'XP'
