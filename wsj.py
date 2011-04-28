# Copyright (C) 2007-2011 Franco M. Luque
# URL: <http://www.cs.famaf.unc.edu.ar/~francolq/>
# For license information, see LICENSE.txt

import itertools
import os

from nltk.corpus.reader import util
from nltk.corpus.reader import bracket_parse
from nltk import tree
from nltk.util import LazyMap

import treebank

word_tags = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS', 'PDT', 
'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB']
currency_tags_words = ['#', '$', 'C$', 'A$']
ellipsis = ['*', '*?*', '0', '*T*', '*ICH*', '*U*', '*RNR*', '*EXP*', '*PPA*', '*NOT*']
punctuation_tags = ['.', ',', ':', '-LRB-', '-RRB-', '\'\'', '``']
punctuation_words = ['.', ',', ':', '-LRB-', '-RRB-', '\'\'', '``', '--', ';', '-', '?', '!', '...', '-LCB-', '-RCB-']
# the tag of -- - ; ... is :
# the tag of ? ! is .
# ' is not punctuation but a POS (possesive pronoun?)
# '-LCB-', '-RCB-' are square brackets
# exception: the tree ['07/wsj_0758.mrg', 74] (antepenultimo) uses simple quotes


def is_ellipsis(s):
    """Returns True if s is an ellipsis tag or leaf.
    """
    return s == '-NONE-' or s.partition('-')[0] in ellipsis


def is_punctuation(s):
    """Returns True if s is a punctuation tag or leaf.
    """
    return s in punctuation_words


class WSJTree(treebank.Tree):
    
    def is_ellipsis(self, s):
        return is_ellipsis(s)
    
    def is_punctuation(self, s):
        return is_punctuation(s)


# TODO: Rename this class to WSJ. 
# TODO: Inherit from treebank.Treebank and move some functionality there.
class WSJSents(bracket_parse.BracketParseCorpusReader):
    
    def __init__(self):
        bracket_parse.BracketParseCorpusReader.__init__(self, 'wsj_comb', '.*')
        fileids = self.fileids()
        self.train_fileids = [s for s in fileids if int(s[:2]) <= 22]
        self.test_fileids = [s for s in fileids if int(s[:2]) == 23]
        self.only_pos = False
    
    def sents(self, fileids=None):
        if self.only_pos:
            f = lambda s: map(lambda x: x[1], s)
        else:
            f = lambda s: map(lambda x: x[0], s)
        return LazyMap(f, self.tagged_sents(fileids))

    def tagged_sents(self, fileids=None):
        # Remove punctuation, ellipsis and currency ($, #) at the same time:
        if self.only_pos:
            f = lambda s: [(x[1], x[1]) for x in filter(lambda x: x[1] in word_tags, s)]
        else:
            f = lambda s: filter(lambda x: x[1] in word_tags, s)
        return LazyMap(f, bracket_parse.BracketParseCorpusReader.tagged_sents(self, fileids))

    def parsed_sents(self, fileids=None):
        def f(t):
            t2 = WSJTree(t)
            #t2.remove_punctuation()
            #t2.remove_ellipsis()
            # Remove punctuation, ellipsis and currency ($, #) at the same time:
            t2.filter_pos(lambda x, y: y in word_tags)
            return t2
        return LazyMap(f, bracket_parse.BracketParseCorpusReader.parsed_sents(self, fileids))

    def only_pos_mode(self, value=True):
        self.only_pos = value


# TODO: remove this class and rename WSJSents to WSJ.
class WSJ(treebank.SavedTreebank):
    default_basedir = 'wsj_comb'
    trees = []
    filename = 'wsj.treebank'
   
    def __init__(self, basedir=None):
        if basedir == None:
            basedir = self.default_basedir
        else:
            basedir = basedir
        treebank.SavedTreebank.__init__(self, self.filename, basedir)
        #self.reader = BracketParseCorpusReader(self.basedir, self.get_files())
   
    def get_files(self):
        l = os.listdir(self.basedir)
        files = []
        for d in l:
            files = files + map(lambda s: d+'/'+s, os.listdir(self.basedir+'/'+d))
        return files
   
    """def parsed(self, files=None):
        if files is None:
            files = self.get_files()
        for (i, t) in itertools.izip(itertools.count(), treebank.SavedTreebank.parsed(self, files)):
            yield WSJTree(t, labels=i)"""
   
    def parsed(self, files=None):
        """
        @param files: One or more WSJ treebank files to be processed
        @type files: L{string} or L{tuple(string)}
        @rtype: iterator over L{tree}
        """
        if files is None:
            files = self.get_files()
        
        # Just one file to process?  If so convert to a tuple so we can iterate
        if isinstance(files, str):
            files = (files,)
        
        size = 0
        for file in files:
            path = os.path.join(self.basedir, file)
            f = open(path)
            i = 0
            t = read_parsed_tb_block(f)
            #print "Parsing", len(t), "trees from file", file
            print "Parsing file", file
            while t != []:
                size += 1
                #yield treebank.Tree(t[0], [file, i])
                yield WSJTree(t[0], [file, i])
                i = i+1
                t = t[1:]
                if t == []:
                    t = read_parsed_tb_block(f)
        print "Finished processing", size, "trees"
    
    def get_tree(self, offset=0):
        t = self.get_trees2(offset, offset+1)[0]
        return t
    
    # Devuelve los arboles que se encuentran en la posicion i con start <= i < end
    def get_trees2(self, start=0, end=None):
        lt = [t for t in itertools.islice(self.parsed(), start, end)]
        return lt
    
    def is_ellipsis(self, s):
        return is_ellipsis(s)
    
    def is_punctuation(self, s):
        return is_punctuation(s)


def test():
    tb = WSJ()
    trees = tb.get_trees()
    return tb


# ROBADO DE nltk 0.8, nltk/corpus/treebank.py, despues eliminado de nltk.

def treebank_bracket_parse(t):
    try:
        return tree.bracket_parse(t)
    except IndexError:
        # in case it's the real treebank format,
        # strip first and last brackets before parsing
        return tree.bracket_parse(t.strip()[1:-1])

def read_parsed_tb_block(stream):
    return [treebank_bracket_parse(t) for t in
            util.read_sexpr_block(stream)]
