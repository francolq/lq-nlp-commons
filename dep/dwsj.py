# Copyright (C) 2007-2011 Franco M. Luque
# URL: <http://www.cs.famaf.unc.edu.ar/~francolq/>
# For license information, see LICENSE.txt

# dwsj.py: Dependency version of the WSJ corpus.

from nltk.corpus.reader import bracket_parse
from nltk.corpus.reader import dependency
from nltk.util import LazyMap

import treebank
import wsj
import wsj10
from dep import depset
from dep import depgraph


class DWSJ(treebank.AbstractTreebank, dependency.DependencyCorpusReader):
    root = 'ptb'
    files = ['ptb.train', 'ptb.val', 'ptb.test']
    train_fileids = files[0]
    test_fileids = files[1]
    valid_tags = wsj.word_tags + wsj.currency_tags_words
    remove_punct = False

    def __init__(self, filename=None):
        if filename:
            self.root = ''
            self.files = filename
            self.train_fileids = filename
            self.test_fileids = filename
        dependency.DependencyCorpusReader.__init__(self, self.root, self.files)

    def sents(self, fileids=None):
        if self.remove_punct:
            f = lambda s: map(lambda x: x[0], s)
            return LazyMap(f, self.tagged_sents(fileids))
        else:
            return dependency.DependencyCorpusReader.sents(self, fileids)

    def tagged_sents(self, fileids=None):
        if self.remove_punct:
            #f = lambda s: filter(lambda x: x[1] in self.valid_tags, s)
            f = lambda s: filter(lambda x: not self.is_punctuation_tag(x[1]), s)
            return LazyMap(f, dependency.DependencyCorpusReader.tagged_sents(self, fileids))
        else:
            return dependency.DependencyCorpusReader.tagged_sents(self, fileids)

    def parsed_sents(self, fileids=None):
        if self.remove_punct:
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
        else:
            def f(t):
                # wrap into depgraph.DepGraph:
                t = depgraph.DepGraph(t)
                # attach depset:
                t.depset = depset.from_depgraph(t)
                return t

        return LazyMap(f, dependency.DependencyCorpusReader.parsed_sents(self, fileids))

    def is_punctuation_tag(self, t):
        return t in wsj.punctuation_tags
        
    def write_deps(self, filename, fileids=None):
        """Writes the dependencies to a text file, one sentence per line.
        """
        f = open(filename, 'w')
        for t in self.parsed_sents(fileids):
            f.write(' '.join(str(d[1]) for d in t.depset.deps)+'\n')
        f.close()


class TaggedDWSJ(DWSJ):
    files = ['ptb.train40k.xtagged40k-10', 'ptb.val.tagged40k', 'ptb.test.tagged40k']
    train_fileids = files[0]
    test_fileids = files[1]


class ToyDWSJ(DWSJ):
    files = ['toy.train', 'toy.val']
    train_fileids = files[0]
    test_fileids = files[1]


class DepWSJ(wsj.WSJSents):
    
    def parsed_sents(self, fileids=None):
        def f(t):
            find_heads(t, label=False)
            t.depset = tree_to_depset(t)
            return t
        return LazyMap(f, wsj.WSJSents.parsed_sents(self, fileids))

    def write_deps(self, filename, fileids=None):
        """Writes the dependencies to a text file, one sentence per line.
        """
        f = open(filename, 'w')
        for t in self.parsed_sents(fileids):
            f.write(' '.join(str(d[1]) for d in t.depset.deps)+'\n')
        f.close()


class DepWSJn(wsj10.WSJnLex):
    
    def __init__(self, max_length, basedir=None, load=True):
        wsj10.WSJnLex.__init__(self, max_length, basedir, load=False)
        self.filename = 'dwsj%02i.treebank' % max_length
        if load:
            self.get_trees()

    def _generate_trees(self):
        trees = wsj10.WSJnLex._generate_trees(self)
        for t in trees:
            # First find the head for each constituent:
            find_heads(t, label=False)
            t.depset = tree_to_depset(t)
        return trees


class DepWSJ10(DepWSJn):
    
    def __init__(self, basedir=None, load=True):
        DepWSJn.__init__(self, 10, basedir, load)


def find_heads(t, label=True):
    """Mark heads in the constituent tree t using the Collins PhD Thesis (1999)
    rules. The heads are marked in every subtree st in the attribute st.head
    (and in st.node if label=True).
    """
    for st in t.subtrees():
        parent = st.node.split('-')[0].split('=')[0]
        # the children may be a tree or a leaf (type string):
        children = [(type(x) is str and x) or x.node.split('-')[0] for x in st]
        st.head = get_head(parent, children)-1
        if label:
            st.node += '['+children[st.head]+']'


def tree_to_depset(t):
    """Returns the DepSet associated to the head marked tree t (with find_heads).
    """
    leave_index = 0
    res = set()
    aux = {}
    # Traverse the tree from the leaves upwards (postorder)
    for p in t.treepositions(order='postorder'):
        st = t[p]
        if isinstance(st, str):
            # We are at leave with index leave_index.
            aux[p] = leave_index
            leave_index += 1
        else:
            # We are at a subtree. aux has the index of the
            # head for each subsubtree.
            head = st.head
            if type(st[head]) is str:
                # index of the leave at deptree[head]
                head_index = aux[p+(head,)]
            else:
                head_index = st[head].head_index
            st.head_index = head_index
            for i in range(len(st)):
                sst = st[i]
                if i == head:
                    pass # skip self dependency
                elif type(sst) is str:
                    res.add((aux[p+(i,)], head_index))
                else:
                    res.add((sst.head_index, head_index))
    res.add((t.head_index, -1))

    return depset.DepSet(len(t.leaves()), sorted(res))


def get_head(label, children):
    """children must be a not empty list. Returns the index of the head,
    starting from 1.
    (rules for the Penn Treebank, taken from p. 239 of Collins thesis).
    The rules for X and NX are not specified by Collins. We use the ones
    at <paste link here> (also at Yamada and Matsumoto 2003).
    (X only appears at wsj_0056.mrg and at wsj_0077.mrg)
    """
    assert children != []
    if len(children) == 1:
        # Used also when label is a POS tag and children is a word.
        res = 1
    elif label == 'NP':
        # Rules for NPs

        # search* returns indexes starting from 1
        # (to avoid confusion between 0 and False):
        res = (children[-1] in wsj.word_tags and len(children)) or \
                searchr(children, set('NN NNP NNS NNPS NNS NX POS JJR'.split())) or \
                searchl(children, 'NP') or \
                searchr(children, set('$ ADJP PRN'.split())) or \
                searchr(children, 'CD') or \
                searchr(children, set('JJ JJS RB QP'.split())) or \
                len(children)
    else:
        rule = head_rules[label]
        plist = rule[1]
        if plist == [] and rule[0] == 'r':
            res = len(children)
        # Redundant:
        #elif plist == [] and rule[0] == 'l':
        #    res = 1
        else:
            res = None
        i, n = 0, len(plist)
        if rule[0] == 'l':
            while i < n and res is None:
                # search* returns indexes starting from 1
                res = searchl(children, plist[i])
                i += 1
        else:
            #assert rule[0] == 'r'
            while i < n and res is None:
                # search* returns indexes starting from 1
                res = searchr(children, plist[i])
                i += 1
        if res is None:
            res = 1

    # Rules for coordinated phrases
    #if 'CC' in [res-2 >= 0 and children[res-2], \
    #            res < len(children) and children[res]]:
    if res-2 >= 1 and children[res-2] == 'CC':
        # On the other case the head doesn't change.
        res -= 2

    return res


def searchr(l, e):
    """As searchl but from right to left. When not None, returns the index
    starting from 1.
    """
    l = l[::-1]
    r = searchl(l, e)
    if r is None:
        return None
    else:
        return len(l)-r+1


def searchl(l, e):
    """Returns the index of the first occurrence of any member of e in l,
    starting from 1 (just for convenience in the usage, see get_head). Returns
    None if there is no occurrence.
    """
    #print 'searchl('+str(l)+', '+str(e)+')'
    if type(e) is not set:
        e = set([e])
    i, n = 0, len(l)
    while i < n and l[i] not in e:
        i += 1
    if i == n:
        return None
    else:
        #return l[i]
        return i+1


head_rules = {'ADJP': ('l', 'NNS QP NN $ ADVP JJ VBN VBG ADJP JJR NP JJS DT FW RBR RBS SBAR RB'.split()), \
 'ADVP': ('r', 'RB RBR RBS FW ADVP TO CD JJR JJ IN NP JJS NN'.split()), \
 'CONJP': ('r', 'CC RB IN'.split()), \
 'FRAG': ('r', []), \
 'INTJ': ('l', []), \
 'LST': ('r', 'LS :'.split()), \
 'NAC': ('l', 'NN NNS NNP NNPS NP NAC EX $ CD QP PRP VBG JJ JJS JJR ADJP FW'.split()), \
 'PP': ('r', 'IN TO VBG VBN RP FW'.split()), \
 'PRN': ('l', []), \
 'PRT': ('r', 'RP'.split()), \
 'QP': ('l', '$ IN NNS NN JJ RB DT CD NCD QP JJR JJS'.split()), \
 'RRC': ('r', 'VP NP ADVP ADJP PP'.split()), \
 'S': ('l', 'TO IN VP S SBAR ADJP UCP NP'.split()), \
 'SBAR': ('l', 'WHNP WHPP WHADVP WHADJP IN DT S SQ SINV SBAR FRAG'.split()), \
 'SBARQ': ('l', 'SQ S SINV SBARQ FRAG'.split()), \
 'SINV': ('l', 'VBZ VBD VBP VB MD VP S SINV ADJP NP'.split()), \
 'SQ': ('l', 'VBZ VBD VBP VB MD VP SQ'.split()), \
 'UCP': ('r', []), \
 'VP': ('l', 'TO VBD VBN MD VBZ VB VBG VBP VP ADJP NN NNS NP'.split()), \
 'WHADJP': ('l', 'CC WRB JJ ADJP'.split()), \
 'WHADVP': ('r', 'CC WRB'.split()), \
 'WHNP': ('l', 'WDT WP WP$ WHADJP WHPP WHNP'.split()), \
 'WHPP': ('r', 'IN TO FW'.split()), \
 'NX': ('r', 'POS NN NNP NNPS NNS NX JJR CD JJ JJS RB QP NP'.split()), \
 'X': ('r', [])
}
