# Copyright (C) 2007-2009 Franco M. Luque
# URL: <http://www.cs.famaf.unc.edu.ar/~francolq/>
# For license information, see LICENSE.txt

import wsj

import itertools


class WSJn(wsj.WSJ):
   
    def __init__(self, n, basedir=None, load=True):
        wsj.WSJ.__init__(self, basedir)
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
        # Con esto elimino puntuacion, ellipsis y $ y # (currency) al mismo tiempo:
        t.filter_tags(lambda x: x in wsj.word_tags)
        return t


class WSJ10(WSJn):
   
    def __init__(self, basedir=None, load=True):
        WSJn.__init__(self, 10, basedir, load)


class WSJ40(WSJn):
   
    def __init__(self, basedir=None, load=True):
        WSJn.__init__(self, 40, basedir, load)


class WSJ10P(wsj.WSJ):
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
        wsj.WSJ.__init__(self, basedir)
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
        t.filter_tags(lambda x: x in self.valid_tags)
        return t

"""
Comparo la version vieja con la nueva:

>>> from wsj10 import *
>>> tbold = WSJ10P(load=False)
>>> tbold.filename = 'wsj10p.treebank.old'
>>> ts = tbold.get_trees()
>>> tb = WSJ10P()

# l son los indices de los arboles con hojas distintas
>>> l = [i for i in range(len(tbold.trees)) if tbold.trees[i].leaves() != tb.trees[i].leaves()]
>>> len(l)
6713
# l2 son los indices de los arboles que cambian algo mas ademas del punto al final. Vemos que quedan pocos, 683.
>>> l2 = [j for j in l if tbold.trees[j].leaves() != tb.trees[j].leaves()[:-1]]
>>> len(l2)
683
# entre los 683 de l2 hay algunos que agregan punto pero no al final sino un lugar antes (despues se suele cerrar comillas). quitamos estos en l3 para quedarnos con los que realmente hacen alguna diferencia:
>>> l3 = [k for k in l2 if tbold.trees[j].leaves()[:-1] != tb.trees[j].leaves()[:-2]]
>>> len(l3)
0
# NO HAY NINGUNO! o sea que son masomenos lo mismo los corpus, PERO SOLO PARA EL CASO DEL WSJ10.
"""


class WSJnTagged(WSJn):
    
    def __init__(self, n, basedir=None, load=True):
        wsj.WSJ.__init__(self, basedir)
        self.n = n
        self.filename = 'wsj%02i.tagged_treebank' % n
        self.tagger = WSJTagger()
        if load:
            self.get_trees()
   
    def _prepare(self, t):
        # quito puntuacion, ellipsis y monedas, sin quitar las hojas:
        #t.remove_punctuation()
        #t.remove_ellipsis()
        #t.filter_tags(lambda x: x not in wsj.currency_tags_words)
        t.filter_subtrees(lambda t: type(t) == str or len([x for x in t.pos() if x[1] in wsj.word_tags]) > 0)
        t.map_leaves(self.tagger.tag)
        return t


class WSJ10Tagged(WSJnTagged):
   
    def __init__(self, basedir=None, load=True):
        WSJnTagged.__init__(self, 10, basedir, load)


class WSJTagger:
   
    filename = '../obj/clusters.nem.32'
    
    def __init__(self):
        f = open(self.filename)
        self.tag_dict = {}
        for l in f:
            l2 = l.split()
            self.tag_dict[l2[0]] = l2[1]+'C'
   
    def tag(self, word):
        return self.tag_dict[word.upper()]


"""
Chequeo del corpus (pa ver si saca los mismos arboles que WSJ10):

>>> from wsj10 import *
>>> tb2 = WSJ10Tagged()
>>> len(tb2.trees)
7412
# significa que faltan arboles... deberian  ser 7422
>>> tb = WSJ10()
>>> l = [i for i in range(len(tb2.trees)) if tb.trees[i].labels != tb2.trees[i].labels]
>>> l[0]
2112
>>> i = l[0]
>>> l[1]
2113
>>> tb.trees[i].labels
['07/wsj_0758.mrg', 74]
>>> tb2.trees[i].labels
['07/wsj_0758.mrg', 75]

QUE BOSTA, SE USAN COMILLAS SIMPLES CUANDO DEBERIAN SER DOBLES:

( (S
    (NP-SBJ (PRP You) )
    (VP (MD might) (RB not)
      (VP (VB find)
        (NP (NN one) )
        (PP-LOC (IN in)
          (NP (DT the) (`` `) (NN Jurisprudence) ('' ') (NN column) ))))
    (. .) ))
"""


class WSJnLex(WSJn):
    
    def __init__(self, n, load=True):
        wsj.WSJ.__init__(self)
        self.n = n
        self.filename = 'wsj%02i.lex_treebank' % n
        self.tagger = WSJTagger()
        if load:
            self.get_trees()
    
    def _prepare(self, t):
        # quito puntuacion, ellipsis y monedas, sin quitar las hojas:
        #t.remove_punctuation()
        #t.remove_ellipsis()
        #t.filter_tags(lambda x: x not in wsj.currency_tags_words)
        t.filter_subtrees(lambda t: type(t) == str or len([x for x in t.pos() if x[1] in wsj.word_tags]) > 0)
        return t


class WSJ10Lex(WSJnLex):
    def __init__(self, load=True):
        WSJnLex.__init__(self, 10, load)

"""
CREO UN ARCHIVO DE TEXTO CON LAS FRASES DEL WSJ10:

>>> from wsj10 import *
>>> tb = WSJ10Lex()
>>> for t in tb.trees:
...     s = string.join(t.leaves())+'\n'
...     f.write(s)
...
>>> f.close()
>>>

"""

def test():
    tb = WSJ10()
    return tb
