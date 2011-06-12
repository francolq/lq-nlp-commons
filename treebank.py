# Copyright (C) 2007-2011 Franco M. Luque
# URL: <http://www.cs.famaf.unc.edu.ar/~francolq/>
# For license information, see LICENSE.txt

# -*- coding: iso-8859-1 -*-

import os
import itertools

from nltk import tree
from nltk.corpus.reader import api
from nltk.util import LazyMap

import util


class Tree(tree.Tree):
    def __new__(cls, nltk_tree=None, labels=None):
        if nltk_tree is None:
            return super(Tree, cls).__new__(cls)
        else:
            return super(Tree, cls).__new__(cls, nltk_tree.node, nltk_tree)
    
    def __init__(self, nltk_tree, labels=None):
        tree.Tree.__init__(self, nltk_tree.node, nltk_tree)
        self.labels = labels
    
    def copy(self, deep=False):
        if not deep:
            #return self.__class__(self, self.labels)
            t = self.__class__(self, self.labels)
        else:
            #return self.__class__(tree.Tree.convert(self), self.labels)
            t = self.__class__(tree.Tree.convert(self), self.labels)
        if hasattr(self, 'depset'):
            t.depset = self.depset
        return t
    
    def map_nodes(self, f):
        lpos = self.treepositions()
        for pos in lpos:
            if isinstance(self[pos], tree.Tree):
                self[pos].node = f(self[pos].node)
            else:
                self[pos] = f(self[pos])
    
    def map_leaves(self, f):
        """
        Maps f to the leaves of the trees.

        @param f: function over strings.
        """
        lpos = self.treepositions('leaves')
        for pos in lpos:
            self[pos] = f(self[pos])

    def map_pos(self, f):
        """
        Maps f to the pairs (word, pos).

        @param f: function over two strings (word and pos) returning a pair.
        """
        lpos = self.treepositions('leaves')
        for pos in lpos:
            st = self[pos[:-1]]
            w, t = st[0], st.node
            st[0], st.node = f(w, t)

    def filter_subtrees(self, f, prune=True):
        """Removes the subtrees that do not satisfy the predicate f.
        XXX: Not done in-place. Internally creates a new tree.
        
        @param f: A predicate function over trees and strings (for the leaves).
        @param prune: If True, remove a subtree if it has no children. If False,
        convert the subtree to a leaf.
        """
        def recursion(t, f):
            if f(t):
                if isinstance(t, tree.Tree):
                    subtrees = []
                    for st in t:
                        st2 = recursion(st, f)
                        if st2 is not None:
                            subtrees += [st2]
                    if subtrees:
                        return tree.Tree(t.node, subtrees)
                    elif prune:
                        return None
                    else:
                        return t.node
                else:
                    # assert isinstance(t, str)
                    return t
            else:
                return None
        t = recursion(self, f)
        if isinstance(t, tree.Tree):
            self.__init__(t, self.labels)
        else:
            self.__init__(tree.Tree(t, []), self.labels)

    def remove_functions(self):
        self.map_nodes(lambda node: node.split('-')[0])
    
    def remove_leaves(self):
        self.filter_subtrees(lambda t: isinstance(t, tree.Tree), prune=False)
    
    def filter_leaves(self, f):
        """Removes from the tree the leaves that do not satisfy f.

        @param f: predicate function over strings.
        """
        self.filter_subtrees(lambda t: isinstance(t, tree.Tree) or f(t))

    def filter_pos(self, f):
        """
        Removes from the tree the pairs (word, pos) that do not satisfy f.
        
        @param f: predicate function over two strings (word and pos).
        """
        def is_pos_node(t):
            #assert t, 'Tree with no leaves.'
            return isinstance(t, tree.Tree) and isinstance(t[0], str)
        def f2(t):
            return not is_pos_node(t) or f(t[0], t.node)
        self.filter_subtrees(f2)
    
    def remove_punctuation(self):
        """Uses self.is_punctuation() that must be overriden in the subclasses.
        """
        self.filter_leaves(lambda s: not self.is_punctuation(s))
    
    def is_punctuation(self, s):
        """To be overriden in the subclasses.
        """
        return False
    
    def remove_ellipsis(self):
        """Uses self.is_ellipsis() that must be overriden in the subclasses.
        """
        self.filter_leaves(lambda s: not self.is_ellipsis(s))
    
    def is_ellipsis(self, s):
        """To be overriden in the subclasses.
        """
        return False
    
    # DEPRECATED: creo que nunca uso esta bosta, aunque podria:
    # Invocar solo sobre arboles que tengan la frase en sus hojas.
    # Largo de la frase sin contar puntuacion ni elementos nulos.
    # FIXME: esta funcion deberia estar en una clase WSJ_Tree(Tree) en wsj.py.
    def length(self):
        t2 = self.copy()
        t2.remove_leaves()
        return len(filter(lambda t: t in self.valid_tags, t2.leaves()))
    
    def dfs(self):
        queue = self.treepositions()
        stack = [queue.pop(0)]
        while stack != []:
            p = stack[-1]
            if queue == [] or queue[0][:-1] != p:
                stack.pop()
                print p, "volviendo"
            else: # queue[0] es hijo de p:
                q = queue.pop(0)
                stack.append(q)
                print p, "yendo"
    
    def labelled_spannings(self, leaves=True, root=True, unary=True):
        queue = self.treepositions()
        stack = [(queue.pop(0),0)]
        j = 0
        result = []
        while stack != []:
            (p,i) = stack[-1]
            if queue == [] or queue[0][:-1] != p:
                # ya puedo devolver spanning de p:
                if isinstance(self[p], tree.Tree):
                    result += [(self[p].node, (i, j))]
                else:
                    # es una hoja:
                    if leaves:
                        result += [(self[p], (i, i+1))]
                    j = i+1
                stack.pop()
            else: # queue[0] es el sgte. hijo de p:
                q = queue.pop(0)
                stack.append((q,j))
        if not root:
            # El spanning de la raiz siempre queda al final:
            result = result[0:-1]
        if not unary:
            result = filter(lambda (l, (i, j)): i != j-1, result)
        return result
    
    def spannings(self, leaves=True, root=True, unary=True):
        """Returns the set of unlabeled spannings.
        """
        queue = self.treepositions()
        stack = [(queue.pop(0),0)]
        j = 0
        result = set()
        while stack != []:
            (p,i) = stack[-1]
            if queue == [] or queue[0][:-1] != p:
                # ya puedo devolver spanning de p:
                if isinstance(self[p], tree.Tree):
                    result.add((i, j))
                else:
                    # es una hoja:
                    if leaves:
                        result.add((i, i+1))
                    j = i+1
                stack.pop()
            else: # queue[0] es el sgte. hijo de p:
                q = queue.pop(0)
                stack.append((q,j))
        if not root:
            # FIXME: seguramente se puede programar mejor:
            result.remove((0,len(self.leaves())))
        if not unary:
            # FIXME: seguramente se puede programar mejor:
            result = set(filter(lambda (x,y): x != y-1, result))
        return result

    def spannings2(self, leaves=True, root=True, unary=True, order=None):
        """TODO: Returns the unlabeled spannings as an ordered list.
        Meant to replace spannings in the future.
        """
        queue = self.treepositions(order)
        stack = [(queue.pop(0),0)]
        j = 0
        result = set()
        while stack != []:
            (p,i) = stack[-1]
            if queue == [] or queue[0][:-1] != p:
                # ya puedo devolver spanning de p:
                if isinstance(self[p], tree.Tree):
                    result.add((i, j))
                else:
                    # es una hoja:
                    if leaves:
                        result.add((i, i+1))
                    j = i+1
                stack.pop()
            else: # queue[0] es el sgte. hijo de p:
                q = queue.pop(0)
                stack.append((q,j))
        if not root:
            # FIXME: seguramente se puede programar mejor:
            result.remove((0,len(self.leaves())))
        if not unary:
            # FIXME: seguramente se puede programar mejor:
            result = set(filter(lambda (x,y): x != y-1, result))
        return result


#class AbstractTreebank(api.SyntaxCorpusReader):
class AbstractTreebank:

    def __init__(self):
        pass
    
    def pquery(self, p, fileids=None, res=1):
        """Returns elements of the treebank that satisfy the predicate p.

        @param p: Predicate that takes a tagged_sent and a parsed_sent.
        @param res: Number of results.
        """
        result = []
        for s, t in zip(self.tagged_sents(fileids), self.parsed_sents(fileids)):
            if p(s, t):
                result.append((s, t))
                res -= 1
            if res == 0:
                if len(result) == 1:
                    return result[0]
                else:
                    return result
        return result
    
    def psentquery(self, p, fileids=None, res=1):
        """Returns sentences of the treebank that satisfy the predicate p.

        @param p: Predicate that takes a tagged_sent.
        @param res: Number of results.
        """
        result = []
        for s in self.tagged_sents(fileids):
            if p(s):
                result.append(s)
                res -= 1
            if res == 0:
                if len(result) == 1:
                    return result[0]
                else:
                    return result
        return result

    def query(self, l=None, fileids=None, res=1):
        """Returns elements of the treebank that satisfy the given conditions.

        @param l: Length of the sentence.
        @param res: Number of results.
        """
        if l is not None:
            return self.pquery(lambda s, t: len(s) == l, fileids, res)
        else:
            return self.pquery(lambda s, t: True, fileids, res)
    
    def vocabulary(self, fileids=None):
        """Returns the set of terminals of all the trees.
        """
        result = set()
        for s in self.sents(fileids):
            result.update(s)

        return result

    def word_freqs(self, fileids=None):
        d = {}
        for s in self.sents(fileids):
            for w in s:
                if w in d:
                    d[w] += 1
                else:
                    d[w] = 1

        return d

    def length_freqs(self):
        d = {}
        for s in self.sents():
            l = len(s)
            if l in d:
                d[l] += 1
            else:
                d[l] = 1

        return d


# TODO: Rename this class to ListTreebank.
class Treebank(AbstractTreebank):
    """List backed treebank. The elements are assumed to be Tree instances.
    """
    trees = None
    
    def __init__(self, trees=None):
        AbstractTreebank.__init__(self)
        if trees is None:
            trees = []
        self.trees = trees
        self.only_pos = False
    
    def get_trees(self):
        return self.trees

    def sents(self, fileids=None):
        if self.only_pos:
            f = lambda t: map(lambda x: x[1], t.pos())
        else:
            f = lambda t: t.leaves()
        # LazyMap from nltk.util:
        return LazyMap(f, self.parsed_sents(fileids))
    
    def tagged_sents(self, fileids=None):
        # LazyMap from nltk.util:
        if self.only_pos:
            f = lambda t: map(lambda x: (x[1], x[1]), t.pos())
        else:
            f = lambda t: t.pos()
        return LazyMap(f,  self.parsed_sents(fileids))

    def parsed_sents(self, fileids=None):
        if self.only_pos:
            # lambda with side effects!:
            #f = lambda t: t.map_pos(lambda x, y: (y, y)) or t
            def f(t):
                t2 = t.copy(deep=True)
                t2.map_pos(lambda x, y: (y, y))
                return t2
            return LazyMap(f, self.get_trees())
        else:
            return self.get_trees()

    def only_pos_mode(self, value=True):
        self.only_pos = value
    
    def sent(self, i):
        return self.trees[i].leaves()
    
    def remove_functions(self):
        map(lambda t: t.remove_functions(), self.trees)
    
    def remove_leaves(self):
        map(lambda t: t.remove_leaves(), self.trees)
    
    def length_sort(self):
        self.trees.sort(lambda x,y: cmp(len(x.leaves()), len(y.leaves())))
    
    def stats(self, filename=None):
        trees = self.trees
        avg_height = 0.0
        words = 0
        # vocabulary = []
        if filename is not None:
            f = open(filename, 'w')
        for t in trees:
            height = t.height()
            length = len(t.leaves())
            if filename is not None:
                f.write(str(length) + '\n')
            avg_height = avg_height + height
            words = words + length
        if filename is not None:
            f.close()
        avg_height = avg_height / len(trees)
        avg_length = float(words) / len(trees)
        return (len(trees), avg_height, avg_length)
    
    def print_stats(self, filename=None):
        (size, height, length) = self.stats(filename)
        #print "Pares arbol oracion:", size
        #print "Altura de arbol promedio:", height
        #print "Largo de oracion promedio:", length
        #print "Vocabulario:", len(self.get_vocabulary())
        print "Trees:", size
        print "Average tree depth:", height
        print "Average sentence length:", length
        print "Vocabulary size:", len(self.get_vocabulary())
    
    def get_productions(self):
#        productions = []
#        for t in self.trees:
#            productions += t.productions()
        def concat(l):
            return reduce(lambda x,y: x + y, l)
        productions = concat([t.productions() for t in self.parsed_sents()])
        
        return productions
        
    def is_punctuation(self, s):
        """To be overriden in the subclasses.
        """
        return False
    
    def is_ellipsis(self, s):
        """To be overriden in the subclasses.
        """
        return False
    
    def find_sent(self, ss):
        """Returns the indexes of the sentences that contains the 
        sequence of words ss.
        XXX: remove or move to AbstractTreebank.
        """
        ss = ' '.join(ss)
        l = []
        for i in range(len(self.trees)):
            s = self.sent(i)
            s = ' '.join(s)
            if ss in s:
                l.append(i)
        return l


EMPTY = Treebank([])


def treebank_from_sentences(S):
    """Returns a treebank with sentences S and trivial trees.
    """
    trees = [Tree(tree.Tree('ROOT', [tree.Tree(x, [x]) for x in s])) for s in S]
    return Treebank(trees)


def load_treebank(filename):
    return util.load_obj(filename)


class SavedTreebank(Treebank):
    trees = []
    
    def __init__(self, filename, basedir):
        self.filename = filename
        self.basedir = basedir
        Treebank.__init__(self)
    
    def get_trees(self):
        if self.trees == []:
            trees = util.load_obj(self.filename)
            if trees is None:
                trees = self._generate_trees()
                util.save_obj(trees, self.filename)
            self.trees = trees
        return self.trees

    def save(self, filename=None):
        if filename is None:
            filename = self.filename
        util.save_obj(self.trees, filename)
    
    def _generate_trees(self):
        print "Parsing treebank..."
        trees = [self._prepare(t) for t in self.parsed()]
        return trees
    
    def _prepare(self, t):
        """To be overriden in the subclasses.
        """
        return t
    
    def parsed(self, files=None):
        """
        Prepared for Penn format. May be overriden.
        
        @param files: One or more treebank files to be processed
        @type files: L{string} or L{tuple(string)}
        @rtype: iterator over L{tree}
        """
        if files is None:
            files = sorted(os.listdir(self.basedir))
        
        # Just one file to process?  If so convert to a tuple so we can iterate
        if isinstance(files, str):
            files = (files,)
        
        for file in files:
            print "Parsing file "+file
            path = os.path.join(self.basedir, file)
            s = open(path).read()
            # i = 0
            for i,t in itertools.izip(itertools.count(), tokenize_paren(s)):
                yield Tree(tree.bracket_parse(t), [file, i])
                # i += 1


def tokenize_paren(s):
    """
    Tokenize the text (separated by parentheses).
    
    @param s: the string or string iterator to be tokenized
    @type s: C{string} or C{iter(string)}
    @return: An iterator over tokens
    """
    k = 0
    t = ""
    for c in s:
        if k >= 1:
            t = t + c

        if c == '(':
            k = k + 1
        elif c == ')':
            k = k - 1
            if k == 0:
                yield t[:-1]
                t = ""
