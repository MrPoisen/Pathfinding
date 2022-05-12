from unittest import TestCase, main

from ex import example2 # needed example
from pypathfinder.Astar import ANode, bestpath
from pypathfinder.fast import CNode, astar_bestpath

class TestAstar(TestCase):
    def test_bestpath1(self):
        start, stop, matrix, solution = example2(ANode, 0)
        def heusterik(node: ANode, args) -> int:
            return abs(node.id[0] - len(matrix[0])) + abs(node.id[1] - len(matrix))
        path = bestpath(start, stop, heusterik)
        self.assertEqual(path[-1].cost, solution)
    
    def test_bestpath2(self):
        start, stop, matrix, solution = example2(ANode, 2)
        def heusterik(node: ANode, args) -> int:
            return abs(node.id[0] - len(matrix[0])) + abs(node.id[1] - len(matrix))
        path = bestpath(start, stop, heusterik)
        self.assertEqual(path[-1].cost, solution)

    def test_cythonbestpath1(self):
        start, stop, matrix, solution = example2(CNode, 0)
        def heusterik(node: CNode, args) -> int:
            return abs(node.id[0] - len(matrix[0])) + abs(node.id[1] - len(matrix))
        path = astar_bestpath(start, stop, heusterik)
        self.assertEqual(path[-1].cost, solution)
    
    def test_cythonbestpath2(self):
        start, stop, matrix, solution = example2(CNode, 2)
        def heusterik(node: CNode, args) -> int:
            return abs(node.id[0] - len(matrix[0])) + abs(node.id[1] - len(matrix))
        path = astar_bestpath(start, stop, heusterik)
        self.assertEqual(path[-1].cost, solution)
    
if __name__ == "__main__":
    main()