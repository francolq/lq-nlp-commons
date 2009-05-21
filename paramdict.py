# Copyright (C) 2007-2009 Franco M. Luque
# URL: <http://www.cs.famaf.unc.edu.ar/~francolq/>
# For license information, see LICENSE.txt

# paramdict.py: ParamDict is a comfortable dictionary with commonly needed
# functions.

class ParamDict:
    
    def __init__(self, d=None, default_val=0.0, count_evidence=False):
        if d is None:
            self.d = {}
        else:
            self.d = d
        self.count_evidence = count_evidence
        if count_evidence:
            self.evidence = {}
        self.default_val = default_val
    
    def set_default_val(self, val):
        self.default_val = val
    
    def val(self, x):
        if x in self.d:
            return self.d[x]
        else:
            return self.default_val
    
    def setVal(self, x, val):
        self.d[x] = val
    
    def add1(self, x):
        add(self.d, x, 1.0)
        if self.count_evidence:
            add(self.evidence, x, 1.0)
    
    def add(self, x, y):
        add(self.d, x, y)
        if self.count_evidence and y > 0.0:
            add(self.evidence, x, 1.0)
    
    def iteritems(self):
        return self.d.iteritems()

# Common procedure used in ParamDict:
def add(dict, x, val):
    if x in dict:
        dict[x] = dict[x] + val
    else:
        dict[x] = val
