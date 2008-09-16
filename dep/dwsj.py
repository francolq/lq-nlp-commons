# dwsj.py: Dependency version of the WSJ corpus.

import deptreebank
import wsj10

class DepWSJ10(wsj10.WSJ10):
    
    
    def __init__(self, basedir=None, load=True):
        wsj10.WSJ10.__init__(self, basedir, load=False)
        self.filename =  'dwsj10.treebank'
        if load:
            self.get_trees()
    
    
    def _generate_trees(self):
        trees = wsj10.WSJ10._generate_trees(self)
        dtrees = [deptreebank.DepTree(t) for t in trees]
        return dtrees
