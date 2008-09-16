# rhead.py: RHEAD baseline for unsupervised dependency parsing.

from . import model
from . import deptree

class RHead(model.DepModel):
    trained = True
    tested = True
    
    def __init__(self, treebank=None):
        model.DepModel.__init__(self, treebank)
        self.Parse = [deptree.rhead_deptree(b.length) for b in self.Gold]


def main():
    import dep.dwsj
    tb = dep.dwsj.DepWSJ10()
    m = RHead(tb)
    m.eval()
