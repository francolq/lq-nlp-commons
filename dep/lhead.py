# lhead.py: LHEAD baseline for unsupervised dependency parsing.

from . import model
from . import deptree

class LHead(model.DepModel):
    trained = True
    tested = True
    
    def __init__(self, treebank=None):
        model.DepModel.__init__(self, treebank)
        self.Parse = [deptree.lhead_deptree(b.length) for b in self.Gold]


def main():
    import dep.dwsj
    tb = dep.dwsj.DepWSJ10()
    m = LHead(tb)
    m.eval()
