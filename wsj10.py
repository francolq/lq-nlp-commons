# Copyright (C) 2007-2011 Franco M. Luque
# URL: <http://www.cs.famaf.unc.edu.ar/~francolq/>
# For license information, see LICENSE.txt

import itertools

from nltk.util import LazyMap

import wsj


class WSJn(wsj.SavedWSJ):
    """Sentences of length <= n after removal of punctuation, ellipsis and
    currency.
    To be replaced by the WSJnLex class soon.
    """

    def __init__(self, n, basedir=None, load=True):
        wsj.SavedWSJ.__init__(self, basedir)
        self.n = n
        self.filename = 'wsj%02i.treebank' % n
        if load:
            self.get_trees()

    def _generate_trees(self):
        print "Parsing treebank..."
        f = lambda t: len(t.leaves()) <= self.n
        m = lambda t: self._prepare(t)
        trees = [t for t in itertools.ifilter(f, itertools.imap(m, self.parsed()))]
        return trees

    def _prepare(self, t):
        t.remove_leaves()
        # Remove punctuation, ellipsis and currency ($, #) at the same time:
        t.filter_leaves(lambda x: x in wsj.word_tags)
        return t

    def tagged_sents(self):
        # LazyMap from nltk.util:
        f = lambda t: [(x,x) for x in t.leaves()]
        return LazyMap(f,  self.get_trees())


class WSJ10(WSJn):

    def __init__(self, basedir=None, load=True):
        WSJn.__init__(self, 10, basedir, load)


class WSJ40(WSJn):

    def __init__(self, basedir=None, load=True):
        WSJn.__init__(self, 40, basedir, load)


class WSJ10P(wsj.SavedWSJ):
    """The 7422 sentences of the WSJ10 treebank but including punctuation.
    """
    # antes era puntuacion pero sin el punto final
    #valid_tags = wsj.word_tags + wsj.punctuation_tags[1:]
    #punctuation_tags = wsj.punctuation_tags[1:]
    # pero no da para dejar afuera el punto porque no solo aparece al final (y es tag de ? y !):
    valid_tags = wsj.word_tags + wsj.punctuation_tags
    punctuation_tags = wsj.punctuation_tags
    stop_punctuation_tags = [',', '.', ':']
    bracket_punctuation_tag_pairs = [('-LRB-', '-RRB-'), ('``', '\'\'')]

    def __init__(self, basedir=None, load=True):
        n = 10
        wsj.SavedWSJ.__init__(self, basedir)
        self.n = n
        self.filename = 'wsj%02ip.treebank' % n
        if load:
            self.get_trees()

    def _generate_trees(self):
        print "Parsing treebank..."
        f = lambda t: len(filter(lambda x: x not in self.punctuation_tags, t.leaves())) <= self.n
        m = lambda t: self._prepare(t)
        trees = [t for t in itertools.ifilter(f, itertools.imap(m, self.parsed()))]
        return trees

    def _prepare(self, t):
        t.remove_leaves()
        # Con esto elimino ellipsis y $ y # (currency) al mismo tiempo:
        t.filter_leaves(lambda x: x in self.valid_tags)
        return t


class WSJnLex(wsj.SavedWSJ):
    """Lexicalized WSJn. Sentences of length <= n after removal of punctuation,
    ellipsis and currency. Will replace the WSJn class soon.
    """

    def __init__(self, n, basedir=None, load=True):
        wsj.SavedWSJ.__init__(self, basedir)
        self.n = n
        self.filename = 'wsj%02i.lex_treebank' % n
        if load:
            self.get_trees()

    def _generate_trees(self):
        print "Parsing treebank..."
        f = lambda t: len(t.leaves()) <= self.n
        m = lambda t: self._prepare(t)
        trees = [t for t in itertools.ifilter(f, itertools.imap(m, self.parsed()))]
        return trees

    def _prepare(self, t):
        # only keep word tags (removes punctuation, ellipsis and currency)
        t.filter_subtrees(lambda t: type(t) == str or len([x for x in t.pos() if x[1] in wsj.word_tags]) > 0)
        return t


class WSJ10Lex(WSJnLex):

    def __init__(self, basedir=None, load=True):
        WSJnLex.__init__(self, 10, basedir, load)


class WSJnTagged(WSJn):
    """WSJ tagged with an unsupervised tagger.
    """

    def __init__(self, n, basedir=None, load=True):
        #wsj.WSJ.__init__(self, basedir)
        WSJn.__init__(self, basedir)
        self.n = n
        self.filename = 'wsj%02i.tagged_treebank' % n
        self.tagger = WSJTagger()
        if load:
            self.get_trees()

    def _prepare(self, t):
        # quito puntuacion, ellipsis y monedas, sin quitar las hojas:
        #t.remove_punctuation()
        #t.remove_ellipsis()
        #t.filter_leaves(lambda x: x not in wsj.currency_tags_words)
        t.filter_subtrees(lambda t: type(t) == str or len([x for x in t.pos() if x[1] in wsj.word_tags]) > 0)
        t.map_leaves(self.tagger.tag)
        return t


class WSJ10Tagged(WSJnTagged):
    """WSJ10 tagged with an unsupervised tagger.
    """

    def __init__(self, basedir=None, load=True):
        WSJnTagged.__init__(self, 10, basedir, load)


class WSJTagger:
    """Unsupervised tagger.
    """

    filename = '../obj/clusters.nem.32'

    def __init__(self):
        f = open(self.filename)
        self.tag_dict = {}
        for l in f:
            l2 = l.split()
            self.tag_dict[l2[0]] = l2[1]+'C'

    def tag(self, word):
        return self.tag_dict[word.upper()]
