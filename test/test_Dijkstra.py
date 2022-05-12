from unittest import TestCase, main

from ex import example1, example2
from pypathfinder.Dijkstra import Node, bestpath
from pypathfinder.fast import CNode, djikstra_bestpath


class TestDijkstra(TestCase):
    def test_bestpath1(self):
        frankfurt, muenchen = example1(Node)
        path = bestpath(frankfurt, muenchen)
        self.assertEqual(path, [Node("Frankfurt"), Node("Würzburg"), Node("Nürnberg"), Node("München")])
        self.assertEqual(path[-1].cost, 487)
    
    def test_bestpath2(self):
        frankfurt, muenchen = example1(Node)
        path = bestpath(frankfurt, muenchen, True)
        self.assertEqual(path, [Node("Frankfurt"), Node("Würzburg"), Node("Nürnberg"), Node("München")])
        self.assertEqual(path[-1].cost, 487)
    
    def test_bestpath3(self):
        start, stop, matrix, solution = example2(Node, 2)
        path = bestpath(start, stop, True)
        self.assertEqual(path[-1].cost, solution)
    
    def test_cythonbestpath1(self):
        frankfurt, muenchen = example1(CNode)
        path = djikstra_bestpath(frankfurt, muenchen)
        self.assertEqual(path, [CNode("Frankfurt"), CNode("Würzburg"), CNode("Nürnberg"), CNode("München")])
        self.assertEqual(path[-1].cost, 487)
    
    def test_cythonbestpath2(self):
        frankfurt, muenchen = example1(CNode)
        path = djikstra_bestpath(frankfurt, muenchen, True)
        self.assertEqual(path, [CNode("Frankfurt"), CNode("Würzburg"), CNode("Nürnberg"), CNode("München")])
        self.assertEqual(path[-1].cost, 487)
    
    def test_cythonbestpath3(self):
        start, stop, matrix, solution = example2(CNode, 2)
        path = djikstra_bestpath(start, stop, True)
        self.assertEqual(path[-1].cost, solution)

if __name__ == "__main__":
    main()