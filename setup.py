# Copyright (C) 2007-2009 Franco M. Luque
# URL: <http://www.cs.famaf.unc.edu.ar/~francolq/>
# For license information, see LICENSE.txt

from distutils.core import setup

setup(name='lq-nlp-commons',
         version='0.1.0',
         description="Franco M. Luque's Common Python Code for NLP",
         author='Franco M. Luque',
         author_email='francolq@famaf.unc.edu.ar',
         url='http://www.cs.famaf.unc.edu.ar/~francolq/',
         packages=['dep'],
         py_modules=['bracketing', 'lbranch', 'paramdict',
            'treebank', 'wsj10', 'cast3lb', 'model', 'rbranch',
            'ubound', 'cast3lb10', 'negra', 'sentence', 'util',
            'eval', 'negra10', 'setup', 'wsj'],
         license='GNU General Public License',
        )
