# Copyright (C) 2007-2011 Franco M. Luque
# URL: <http://www.cs.famaf.unc.edu.ar/~francolq/>
# For license information, see LICENSE.txt

from itertools import izip

import bracketing

count_fullspan_bracket = True
count_length_2 = True
count_length_2_1 = False

# Calculo de precision, recall y F1 para dos Bracketings:
def eval(Gold, Parse, output=True, short=False, long=False):
    assert len(Gold) == len(Parse)

    # Medidas sumando brackets y despues promediando:
    brackets_ok = 0
    brackets_parse = 0
    brackets_gold = 0
    
    for gb, pb in izip(Gold, Parse):
        l = gb.length
        if count_length_2_1 or (count_length_2 and l == 2) or l >= 3:
            # Medidas sumando brackets y despues promediando:
            (b_ok, b_p, b_g) = measures(gb, pb)
            brackets_ok += b_ok
            brackets_parse += b_p
            brackets_gold += b_g
            
            """# Medidas sumando brackets y despues promediando:
            brackets_ok += n
            brackets_parse += len(p)
            brackets_gold += len(g)"""
    
    m = float(len(Gold))
    Prec = float(brackets_ok) / float(brackets_parse)
    Rec = float(brackets_ok) / float(brackets_gold)
    F1 = 2*(Prec*Rec)/(Prec+Rec)
    if output and not short:
        print "Cantidad de arboles:", m
        print "Medidas sumando todos los brackets:"
        print "  Precision: %2.1f" % (100*Prec)
        print "  Recall: %2.1f" % (100*Rec)
        print "  Media harmonica F1: %2.1f" % (100*F1)
        if long:
            print "Brackets parse:", brackets_parse
            print "Brackets gold:", brackets_gold
            print "Brackets ok:", brackets_ok
    elif output and short:
        print "F1 =", F1
    else:
        return (m, Prec, Rec, F1)


def string_measures(gs, ps):
    gb = bracketing.string_to_bracketing(gs)
    pb = bracketing.string_to_bracketing(ps)
    return measures(gb, pb)


# FIXME: hacer andar con frases de largo 1!
# devuelve la terna (brackets_ok, brackets_parse, brackets_gold)
# del i-esimo arbol. Se usa para calcular las medidas 
# micro-promediadas.
def measures(gb, pb):
    g, p = gb.brackets, pb.brackets
    n = bracketing.coincidences(gb, pb)
    if count_fullspan_bracket:
        return (n+1, len(p)+1, len(g)+1)
    else:
        return (n, len(p), len(g))


# TODO: esta funcion es util, podria pasar a model.BracketingModel.
# goldtb debe ser un treebank, parse una lista de bracketings.
def eval_label(label, goldtb, parse):
    Rec = 0.0
    brackets_ok = 0
    brackets_gold = 0
    
    bad = []
    
    for gt, pb in izip(goldtb.trees, parse):
        g = set(x[1] for x in gt.labelled_spannings(leaves=False, root=False, unary=False) if x[0] == label)
        gb = bracketing.Bracketing(pb.length, g, start_index=0)
        
        n = bracketing.coincidences(gb, pb)
        if len(g) > 0:
            rec = float(n) / float(len(g))
            bad += [difference(gb, pb)]
        else:
            rec = 1.0
            bad += [set()]
        Rec += rec
        
        brackets_ok += n
        brackets_gold += len(g)
        
    m = len(parse)
    Rec = Rec / float(m)
    
    print "Recall:", Rec
    print "Brackets gold:", brackets_gold
    print "Brackets ok:", brackets_ok
    
    return (Rec, bad)


# Conj. de brackets que estan en b1 pero no en b2
# los devuelve con indices comenzando del 0.
def difference(b1, b2):
    s1 = set(map(lambda (x, y): (x - b1.start_index, y - b1.start_index), b1.brackets))
    s2 = set(map(lambda (x, y): (x - b2.start_index, y - b2.start_index), b2.brackets))
    return s1 - s2


class Tester:
    #count_length_2 = True
    #count_length_2_1 = False
    ignore_punct = True

    def __init__(self, parser, tb):
        """
        @param parser: An object that has a method parser.parse(s) where s is
        a POS tagged sentence (a list with elements of the form (word, tag)).
        """
        self.parser = parser
        #if tb == None:
        #    tb = dwsj.DepWSJ10()
        self.tb = tb
        #if hasattr(tb, 'test_fileids'):
        self.fileids = tb.test_fileids
        #else:
        #    self.fileids = None

    def eval(self, output=True, short=False, long=False, max_length=None):
        #Gold = self.Gold
        self.Parse = []
        self.Times = []
        self.TimesTable = {}
        self.Count = 0
        self.Directed = 0.0
        self.Undirected = 0.0

        i = 0
        #p = util.Progress('Parsed', 0, -1000000)
        out = 'Parsed {0}. Partial results: DA=??.? UA=??.?'.format(i)
        print out,
        sys.stdout.flush()
        outl = len(out)+1
        tb = self.tb
        fileids = self.fileids
        #for t, s in zip(tb.parsed_sents(fileids), tb.tagged_sents(fileids)):
        for t in tb.parsed_sents(fileids):
            s = t.pos()
            l = len(s)
            #if (max_length is None or l <= max_length) \
            #        and (self.count_length_2_1 or (self.count_length_2 and l == 2) or l >= 3):
            (count, directed, undirected) = self.measures(t, s)
            self.Count += count
            self.Directed += directed
            self.Undirected += undirected
            #else:
            #    self.Parse += [None]
            #    self.Times += [None]
            i += 1
            #p.next()
            if self.Count == 0:
                out = 'Parsed {0}. Partial results: DA=??.? UA=??.?'.format(i)
            else:
                out = 'Parsed {0}. Partial results: DA={1:2.2f} UA={2:2.2f}'.format(i, 100*self.Directed/self.Count, 100*self.Undirected/self.Count)
            print ('\b'*outl)+out,
            sys.stdout.flush()
            outl = len(out)+1

        Directed = self.Directed / self.Count
        Undirected = self.Undirected / self.Count

        if output and not short:
            print ''
            #print '  Directed Accuracy: {0:2.2f}'.format(100*Directed)
            #print '  Undirected Accuracy: {0:2.2f}'.format(100*Undirected)
            print 'Unlabeled attachment score: {0} / {1} * 100 = {2:2.2f} %'.format(int(self.Directed), self.Count, 100*Directed)
        elif output and short:
            print "L =", Directed, "UL =", Undirected

    def measures(self, t, s):
        #g, p = self.Gold[i].deps, self.Parse[i].deps
        #g, p = t.depset.deps, self.parser.parse(t.leaves())
        g = t.depset.deps
        n = t.depset.length
        t0 = time.clock()
        p = self.parser.parse(s)
        t1 = time.clock()
        self.Times += [t1 - t0]
        self.TimesTable[n] = self.TimesTable.get(n, []) + [t1 - t0]
        self.Parse += [p]

        if self.ignore_punct:
            g = [d for w, d in zip(s, g) if not self.tb.is_punctuation_tag(w[1])]
            p = [d for w, d in zip(s, p) if not self.tb.is_punctuation_tag(w[1])]
            n = len(g)

        d, u = 0, 0
        for (a, b) in g:
            b1 = (a, b) in p
            b2 = (b, a) in p
            if b1:
                d += 1
            if b1 or b2:
                u += 1

        return (n, d, u)

    def print_time_stats(self):
        print 'Length'.ljust(20)+'Count'.ljust(20)+'Avg. time (sec.)'.ljust(20)
        #+'Variance'.ljust(20)
        table = self.TimesTable
        keys = table.keys()
        m, n = min(keys), max(keys)+1
        for i in range(m, n):
            times = table.get(i, [])
            if times:
                count = len(times)
                avg = sum(times) / len(times)
                print '{0}'.format(i).ljust(20)+'{0}'.format(count).ljust(20)+'{0}'.format(avg).ljust(20)
            else:
                print '{0}'.format(i).ljust(20)+'N/D'
    