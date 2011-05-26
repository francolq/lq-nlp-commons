# Copyright (C) 2007-2011 Franco M. Luque
# URL: <http://www.cs.famaf.unc.edu.ar/~francolq/>
# For license information, see LICENSE.txt

# util.py: Some utilities, mainly for serialization (pickling) of objects.

import os
import pickle
import sys

import nltk


obj_basedir = 'lq-nlp-commons'


def write_file(filename, content):
    f = open(filename, 'w')
    f.write(content)
    f.close()


def read_file(filename):
    f = open(filename)
    content = f.read()
    f.close()
    return content


# XXX: trabaja con listas aunque podria hacerse con set.
def powerset(s):
    if len(s) == 0:
        return [[]]
    else:
        e = s[0]
        p = powerset(s[1:])
        return p + map(lambda x: x+[e], p)


# me fijo si un bracketing no tiene cosas que se cruzan
def tree_consistent(b):
    """FIXME: move this to the bracketing package.
    """
    def crosses((a,b),(c,d)):
        return (a < c and c < b and b < d) or (c < a and a < d and d < b)

    for i in range(len(b)):
        for j in range(i+1,len(b)):
            if crosses(b[i], b[j]):
                return False
    return True


def get_obj_basedir():
    try:
        return nltk.data.find(obj_basedir)
    except LookupError:
        os.mkdir(os.path.join(nltk.data.path[0], obj_basedir))
        return nltk.data.find(obj_basedir)


# Guarda un objeto en un archivo, para luego ser cargado con load_obj.
def save_obj(object, filename):
    path = os.path.join(get_obj_basedir(), filename)
    f = open(path, 'w')
    pickle.dump(object, f, pickle.HIGHEST_PROTOCOL)
    f.close()


# Carga un objeto guardado en un archivo con save_obj.
def load_obj(filename):
    path = os.path.join(get_obj_basedir(), filename)
    try:
        f = open(path, 'r')
        object = pickle.load(f)
        f.close()
    except IOError:
        object = None
    return object


# Carga una lista de objetos guardados en un archivo usando ObjectSaver.
def load_objs(filename):
    path = os.path.join(get_obj_basedir(), filename)
    try:
        f = open(path, 'r')
        objects = []
        try:
            while True:
                objects += [pickle.load(f)]
        except EOFError: # It will always be thrown
            f.close()
    except IOError:
        objects = None
    return objects


class ObjectSaver:

    # Si el archivo existe, lo abre, lo lee y comienza a escribir al final
    def __init__(self, filename):
        path = os.path.join(get_obj_basedir(), filename)
        self.f = open(path, 'a+')
        self.orig_objs = []
        try:
            while True:
                self.orig_objs += [pickle.load(self.f)]
        except EOFError: # It will always be thrown
            pass
    
    def save_obj(self, object):
        pickle.dump(object, self.f, pickle.HIGHEST_PROTOCOL)
        
    def flush(self):
        self.f.flush()

    def close(self):
        self.f.close()


class Progress:
    """
    Helper class to ouput to stdout a fancy indicator of the progress of something.
    See model.Model for an example of usage.

    >>> p = Progress('Parsed', 0, 200)
    Parsed   0 of 200
    >>> p.next()
      1 of 200
    >>> p.next()
      2 of 200
    """
    
    def __init__(self, prefix, n_init, n_max):
        m = len(str(n_max))
        o = "%"+str(m)+"d of "+str(n_max)
        self.i = 0
        print prefix, o % self.i,
        sys.stdout.flush()
        self.o = ("\b"*(2*m+5)) + o

    def next(self):
        self.i += 1
        print self.o % self.i,
        sys.stdout.flush()
