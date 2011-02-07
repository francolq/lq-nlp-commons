# Copyright (C) 2007-2011 Franco M. Luque
# URL: <http://www.cs.famaf.unc.edu.ar/~francolq/>
# For license information, see LICENSE.txt

dist:
	python setup.py sdist

clean:
	rm -f `find . -name '*.pyc'`
	rm -f `find . -name '*~'`
	rm -f MANIFEST
	rm -rf dist
